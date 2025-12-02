import json
import logging
import os
import pathlib
import uuid
from collections.abc import AsyncGenerator

from cleanlab_codex import Client, Project
from codex.types import ProjectValidateResponse
from dotenv import load_dotenv
from fastapi import HTTPException
from pydantic_ai import (
    Agent,
    CallToolsNode,
    ModelMessage,
    ModelRequest,
    ModelRequestNode,
    ModelSettings,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
)
from pydantic_ai.messages import ModelResponse, ModelResponse as PydanticModelResponse
from pydantic_ai.usage import RequestUsage
from pydantic_ai.models.openai import OpenAIChatModel

from airline_agent.backend.schemas.message import (
    AssistantMessage,
    EvalResult,
    MessageMetadata,
    ToolCall,
    ToolCallMessage,
    UserMessage,
)
from airline_agent.backend.schemas.run import Run, RunStatus
from airline_agent.backend.schemas.run_event import (
    RunEvent,
    RunEventObject,
    RunEventThreadMessage,
    RunEventThreadRunCompleted,
    RunEventThreadRunFailed,
    RunEventThreadRunInProgress,
)
from airline_agent.cleanlab_utils.consult_utils import (
    consult_cleanlab,
    update_prompt_with_guidance,
)
from airline_agent.cleanlab_utils.validate_utils import (
    generate_tool_fallback_response,
    get_tools_in_openai_format,
    run_cleanlab_validation_logging_tools,
    validate_tool_call_request,
)
from airline_agent.constants import AGENT_INSTRUCTIONS, AGENT_MODEL
from airline_agent.tools.booking import BookingTools
from airline_agent.tools.knowledge_base import KnowledgeBase

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def create_agent(kb: KnowledgeBase, booking: BookingTools) -> Agent:
    """Create the airline support agent."""
    model = OpenAIChatModel(model_name=AGENT_MODEL, settings=ModelSettings(temperature=0.0))
    return Agent(
        model=model,
        instructions=AGENT_INSTRUCTIONS,
        toolsets=[kb.tools, booking.tools],
    )


def get_cleanlab_project() -> Project:
    """Retrieve the configured Cleanlab project."""
    cleanlab_project_id = os.getenv("CLEANLAB_PROJECT_ID")
    if not cleanlab_project_id:
        msg = "CLEANLAB_PROJECT_ID environment variable is not set"
        raise ValueError(msg)
    return Client().get_project(cleanlab_project_id)


kb = KnowledgeBase(
    kb_path=str(pathlib.Path(__file__).parents[4] / "data/kb.json"),
    vector_index_path=str(pathlib.Path(__file__).parents[4] / "data/vector-db"),
)
booking = BookingTools()
project = get_cleanlab_project()
agent = create_agent(kb, booking)

thread_to_messages: dict[str, list[ModelMessage]] = {}
cleanlab_enabled_by_thread: dict[str, bool] = {}


async def airline_chat_streaming(
    message: UserMessage,
    *,
    cleanlab_enabled: bool,
    stream_intermediate_messages: bool,
) -> AsyncGenerator[RunEvent]:
    run_id = uuid.uuid4()
    thread_id = message.thread_id

    if thread_id not in cleanlab_enabled_by_thread:
        cleanlab_enabled_by_thread[thread_id] = cleanlab_enabled
    elif cleanlab_enabled_by_thread[thread_id] != cleanlab_enabled:
        raise HTTPException(
            status_code=400,
            detail="Cleanlab enabled state cannot be changed after the thread has started",
        )

    yield RunEventThreadRunInProgress(
        id=run_id,
        object=RunEventObject.THREAD_RUN_IN_PROGRESS,
        data=Run(
            id=run_id,
            status=RunStatus.IN_PROGRESS,
            thread_id=message.thread_id,
        ),
    )

    if thread_id not in thread_to_messages:
        thread_to_messages[thread_id] = []

    current_tool_calls: dict[str, ToolCall] = {}

    original_user_query = message.content
    if cleanlab_enabled:
        guidance = consult_cleanlab(original_user_query, thread_to_messages[thread_id])
        user_prompt = update_prompt_with_guidance(original_user_query, guidance)
    else:
        user_prompt = original_user_query

    original_message_history = thread_to_messages[thread_id].copy()
    # Store fallback responses for blocked tool calls (keyed by tool_call_id)
    blocked_tool_call_fallbacks: dict[str, str] = {}
    # Track if we should skip the rest of the run and return fallback directly
    should_return_fallback_directly = False
    fallback_to_return = None
    
    try:
        async with agent.iter(user_prompt=user_prompt, message_history=original_message_history) as run:
            async for node in run:
                # If we should return fallback directly, break out of the loop early
                if should_return_fallback_directly:
                    logger.warning(
                        "[cleanlab] 🛑 Breaking out of run loop early - tool call was guardrailed, will return fallback directly"
                    )
                    break
                if isinstance(node, CallToolsNode):
                    response = node.model_response
                    if response.finish_reason == "tool_call":
                        text_content = ""
                        tool_call_parts_to_validate = []
                        
                        for response_part in response.parts:
                            if isinstance(response_part, TextPart):
                                text_content += response_part.content
                            elif isinstance(response_part, ToolCallPart):
                                tool_call_parts_to_validate.append(response_part)
                                current_tool_calls[response_part.tool_call_id] = ToolCall(
                                    tool_call_id=response_part.tool_call_id,
                                    tool_name=response_part.tool_name,
                                    arguments=json.dumps(response_part.args),
                                )

                        # Validate tool call requests if cleanlab is enabled
                        if cleanlab_enabled and tool_call_parts_to_validate:
                            # Get current message history from run context
                            current_message_history = run.ctx.state.message_history
                            
                            # Calculate what's new (everything after original_message_history)
                            new_messages = current_message_history[len(original_message_history):]
                            
                            # Filter out any tool call requests from new_messages (we're validating them)
                            # We want: user query, but NOT the tool call request being validated
                            new_messages_without_tool_call = []
                            for msg in new_messages:
                                if isinstance(msg, ModelResponse):
                                    # Check if this message contains the tool calls we're validating
                                    has_target_tool_calls = any(
                                        isinstance(part, ToolCallPart) and part.tool_call_id in [tc.tool_call_id for tc in tool_call_parts_to_validate]
                                        for part in msg.parts
                                    )
                                    if not has_target_tool_calls:
                                        new_messages_without_tool_call.append(msg)
                                else:
                                    # Keep non-ModelResponse messages (like ModelRequest with user query)
                                    new_messages_without_tool_call.append(msg)
                            
                            # Validate each tool call request
                            blocked_tool_calls = set()
                            for tool_call_part in tool_call_parts_to_validate:
                                tool_arguments = json.loads(json.dumps(tool_call_part.args)) if hasattr(tool_call_part, 'args') else {}
                                
                                logger.info(
                                    "[cleanlab] Validating tool call request: %s with arguments: %s",
                                    tool_call_part.tool_name,
                                    json.dumps(tool_arguments),
                                )
                                
                                is_valid, validation_result = validate_tool_call_request(
                                    project=project,
                                    tool_call_id=tool_call_part.tool_call_id,
                                    tool_name=tool_call_part.tool_name,
                                    tool_arguments=tool_arguments,
                                    query=original_user_query,
                                    message_history=original_message_history,
                                    new_messages=new_messages_without_tool_call,
                                    tools=get_tools_in_openai_format(agent),
                                    thread_id=thread_id,
                                )
                                
                                if not is_valid and validation_result:
                                    logger.warning(
                                        "[cleanlab] ⚠️ TOOL CALL GUARDRAILED: Tool call request validation FAILED for %s (tool_call_id: %s)",
                                        tool_call_part.tool_name,
                                        tool_call_part.tool_call_id,
                                    )
                                    logger.info(
                                        "[cleanlab] Tool call details - name: %s, arguments: %s, should_guardrail: %s",
                                        tool_call_part.tool_name,
                                        json.dumps(tool_arguments),
                                        validation_result.should_guardrail,
                                    )
                                    blocked_tool_calls.add(tool_call_part.tool_call_id)
                                    
                                    # Generate fallback response for this blocked tool call
                                    try:
                                        logger.info(
                                            "[cleanlab] 🔄 Starting fallback generation for blocked tool call %s...",
                                            tool_call_part.tool_name,
                                        )
                                        fallback_response = await generate_tool_fallback_response(
                                            agent=agent,
                                            tool_name=tool_call_part.tool_name,
                                            tool_arguments=tool_arguments,
                                            original_query=original_user_query,
                                            message_history=thread_to_messages[thread_id],
                                            validation_result=validation_result,
                                        )
                                        # Store fallback for this tool_call_id to use when we see the tool result
                                        blocked_tool_call_fallbacks[tool_call_part.tool_call_id] = fallback_response
                                        
                                        # Parse the fallback JSON to extract the message
                                        try:
                                            fallback_json = json.loads(fallback_response)
                                            fallback_message = fallback_json.get("message", fallback_response)
                                        except (json.JSONDecodeError, AttributeError):
                                            fallback_message = fallback_response
                                        
                                        # Store the fallback message to return directly (skip tool execution and agent response)
                                        fallback_to_return = fallback_message
                                        should_return_fallback_directly = True
                                        
                                        logger.info(
                                            "[cleanlab] ✅ Generated and stored fallback for blocked tool call %s (tool_call_id: %s)",
                                            tool_call_part.tool_name,
                                            tool_call_part.tool_call_id,
                                        )
                                        logger.info(
                                            "[cleanlab] Fallback message to return: %s",
                                            fallback_message[:500] if len(fallback_message) > 500 else fallback_message,
                                        )
                                        logger.warning(
                                            "[cleanlab] 🛑 Tool call was guardrailed. Will return fallback directly and skip tool execution + agent response generation."
                                        )
                                        
                                    except Exception as e:
                                        logger.exception(
                                            "[cleanlab] ❌ Error generating fallback for blocked tool call %s: %s",
                                            tool_call_part.tool_name,
                                            e,
                                        )
                            
                            if blocked_tool_calls:
                                logger.info(
                                    "[cleanlab] %d tool call(s) were blocked. Fallbacks will replace tool results.",
                                    len(blocked_tool_calls),
                                )
                            
                            # If we should return fallback directly, break out of the loop to skip tool execution
                            if should_return_fallback_directly:
                                logger.warning(
                                    "[cleanlab] 🛑 Breaking out of run loop - tool call was guardrailed, will return fallback directly and skip tool execution"
                                )
                                break

                        if text_content and stream_intermediate_messages:
                            yield RunEventThreadMessage(
                                id=run_id,
                                object=RunEventObject.THREAD_MESSAGE,
                                data=AssistantMessage(
                                    thread_id=thread_id,
                                    content=text_content,
                                ),
                            )

                elif isinstance(node, ModelRequestNode) and current_tool_calls:
                    request = node.request
                    for i, request_part in enumerate(request.parts):
                        if isinstance(request_part, ToolReturnPart) and request_part.tool_call_id in current_tool_calls:
                            tool_call = current_tool_calls[request_part.tool_call_id]
                            tool_result = request_part.model_response_str()
                            tool_arguments = json.loads(tool_call.arguments) if isinstance(tool_call.arguments, str) else tool_call.arguments

                            # Check if this tool call was blocked and we have a fallback
                            tool_result_replaced = False
                            if cleanlab_enabled and request_part.tool_call_id in blocked_tool_call_fallbacks:
                                fallback_result = blocked_tool_call_fallbacks[request_part.tool_call_id]
                                logger.warning(
                                    "[cleanlab] 🔄 REPLACING TOOL RESULT: Tool call %s (tool_call_id: %s) was blocked, injecting fallback",
                                    request_part.tool_name,
                                    request_part.tool_call_id,
                                )
                                logger.info(
                                    "[cleanlab] Original tool result: %s",
                                    tool_result[:200] if len(tool_result) > 200 else tool_result,
                                )
                                logger.info(
                                    "[cleanlab] Fallback to inject: %s",
                                    fallback_result[:200] if len(fallback_result) > 200 else fallback_result,
                                )
                                
                                # Create ModelResponse with fallback content
                                fallback_model_response = PydanticModelResponse(
                                    parts=[TextPart(content=fallback_result)],
                                    usage=RequestUsage(input_tokens=0, output_tokens=0),
                                    model_name=None,
                                    timestamp=None,
                                    provider_name="cleanlab_fallback",
                                    finish_reason="stop",
                                )
                                
                                # Monkey-patch the model_response_str method to return the fallback
                                # This is the most reliable way since we can't modify ToolReturnPart's internal state
                                original_model_response_str = request_part.model_response_str
                                
                                def fallback_model_response_str():
                                    return fallback_result
                                
                                # Replace the method on this instance
                                request_part.model_response_str = fallback_model_response_str
                                
                                # Verify it works
                                if request_part.model_response_str() == fallback_result:
                                    tool_result_replaced = True
                                    logger.info(
                                        "[cleanlab] ✅ Successfully monkey-patched model_response_str() for %s to return fallback",
                                        request_part.tool_name,
                                    )
                                    logger.info(
                                        "[cleanlab] Agent will now see fallback tool result and should generate a response"
                                    )
                                else:
                                    logger.error(
                                        "[cleanlab] ❌ CRITICAL: Monkey-patch verification failed for %s. Got: %s, Expected: %s",
                                        request_part.tool_name,
                                        request_part.model_response_str()[:100],
                                        fallback_result[:100],
                                    )
                                    # Restore original method
                                    request_part.model_response_str = original_model_response_str
                            
                            # Only yield tool call message if result was NOT replaced
                            if not tool_result_replaced:
                                yield RunEventThreadMessage(
                                    id=run_id,
                                    object=RunEventObject.THREAD_MESSAGE,
                                    data=ToolCallMessage(
                                        thread_id=thread_id,
                                        content=ToolCall(
                                            tool_call_id=request_part.tool_call_id,
                                            tool_name=request_part.tool_name,
                                            arguments=json.dumps(tool_arguments),
                                            result=request_part.model_response_str(),
                                        ),
                                    ),
                                )
                            del current_tool_calls[request_part.tool_call_id]
                            
                            if tool_result_replaced:
                                logger.info(
                                    "[cleanlab] ✅ Tool result replaced for %s.",
                                    request_part.tool_name,
                                )

            # If we should return fallback directly, do so and skip the rest
            if should_return_fallback_directly and fallback_to_return:
                logger.warning(
                    "[cleanlab] 🛑 Returning fallback directly and skipping agent response generation. Fallback: %s",
                    fallback_to_return[:200] if len(fallback_to_return) > 200 else fallback_to_return,
                )
                
                # Update message history to include the user query and fallback response
                updated_history = thread_to_messages[thread_id].copy()
                # Add user message
                from pydantic_ai.messages import UserPromptPart
                user_request = ModelRequest(parts=[UserPromptPart(content=user_prompt)])
                updated_history.append(user_request)
                # Add fallback as assistant response (but don't add tool call or tool result)
                # Use PydanticModelResponse which is already imported at the top as ModelResponse
                fallback_response_msg = PydanticModelResponse(
                    parts=[TextPart(content=fallback_to_return)],
                    finish_reason="stop",
                )
                updated_history.append(fallback_response_msg)
                thread_to_messages[thread_id] = updated_history
                
                # Yield the fallback as the final response
                # IMPORTANT: This is a recovery agent response, NOT the original LLM's output
                # It should NOT be validated again - it's already a safe fallback generated by the recovery agent
                # We're bypassing ALL validation here by returning early and skipping run_cleanlab_validation_logging_tools()
                yield RunEventThreadMessage(
                    id=run_id,
                    object=RunEventObject.THREAD_MESSAGE,
                    data=AssistantMessage(
                        thread_id=thread_id,
                        content=fallback_to_return,
                        metadata=MessageMetadata(
                            guardrailed=True,
                            scores={},
                            # This is a recovery response - no validation needed
                        ),
                    ),
                )
                logger.warning(
                    "[cleanlab] ✅ Returned recovery agent fallback response directly (BYPASSED all validation - recovery agent output is trusted)"
                )
                
                # Skip the rest of the run processing
                yield RunEventThreadRunCompleted(
                    id=run_id,
                    object=RunEventObject.THREAD_RUN_COMPLETED,
                    data=Run(
                        id=run_id,
                        status=RunStatus.COMPLETED,
                        thread_id=thread_id,
                    ),
                )
                return

            # Log when we're about to check final response
            logger.info(
                "[cleanlab] Run completed. Checking final response. run.result is None: %s",
                run.result is None,
            )
            if run.result is not None:
                logger.info(
                    "[cleanlab] Final response output: %s",
                    run.result.output[:200] if len(run.result.output) > 200 else run.result.output,
                )
            
            if run.result is not None and cleanlab_enabled:
                updated_message_history, final_response, validation_result = run_cleanlab_validation_logging_tools(
                    project=project,
                    query=original_user_query,
                    result=run.result,
                    message_history=original_message_history,
                    tools=get_tools_in_openai_format(agent),
                    thread_id=thread_id,
                    additional_metadata={f"applied_guidance_{i}": guidance for i, guidance in enumerate(guidance)}
                    if guidance
                    else None,
                )
                yield RunEventThreadMessage(
                    id=run_id,
                    object=RunEventObject.THREAD_MESSAGE,
                    data=AssistantMessage(
                        thread_id=thread_id,
                        content=final_response,
                        metadata=MessageMetadata(
                            original_llm_response=run.result.output,
                            is_expert_answer=validation_result.expert_answer is not None,
                            guardrailed=validation_result.should_guardrail,
                            escalated_to_sme=validation_result.escalated_to_sme,
                            scores=_format_eval_results(validation_result),
                            log_id=validation_result.log_id,
                            guardrailed_fallback=validation_result.guardrailed_fallback,
                        ),
                    ),
                )
                thread_to_messages[thread_id] = updated_message_history
            else:
                final_response = run.result.output if run.result is not None else ""
                yield RunEventThreadMessage(
                    id=run_id,
                    object=RunEventObject.THREAD_MESSAGE,
                    data=AssistantMessage(
                        thread_id=thread_id,
                        content=final_response,
                    ),
                )
                thread_to_messages[thread_id] = run.ctx.state.message_history.copy()

        yield RunEventThreadRunCompleted(
            id=run_id,
            object=RunEventObject.THREAD_RUN_COMPLETED,
            data=Run(
                id=run_id,
                status=RunStatus.COMPLETED,
                thread_id=thread_id,
            ),
        )

    except Exception:
        logger.exception("Error in airline chat streaming")
        yield RunEventThreadRunFailed(
            id=run_id,
            object=RunEventObject.THREAD_RUN_FAILED,
            data=Run(
                id=run_id,
                status=RunStatus.FAILED,
                thread_id=thread_id,
            ),
        )
        raise


def _format_eval_results(
    validation_result: ProjectValidateResponse,
) -> dict[str, EvalResult]:
    eval_scores = {
        eval_key: EvalResult.model_validate(eval_result.model_dump())
        for eval_key, eval_result in validation_result.eval_scores.items()
    }
    deterministic_guardrails_results = (
        {
            guardrail_key: EvalResult(
                score=0.0 if guardrail_result.should_guardrail else None,
                triggered=guardrail_result.should_guardrail,
                triggered_guardrail=guardrail_result.should_guardrail,
            )
            for guardrail_key, guardrail_result in validation_result.deterministic_guardrails_results.items()
        }
        if validation_result.deterministic_guardrails_results is not None
        else {}
    )
    return {**eval_scores, **deterministic_guardrails_results}
