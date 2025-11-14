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
    ModelRequestNode,
    ModelSettings,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
)
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
    get_tools_in_openai_format,
    run_cleanlab_validation_logging_tools,
)
from airline_agent.constants import AGENT_INSTRUCTIONS, AGENT_MODEL
from airline_agent.tools.booking import BookingTools
from airline_agent.tools.knowledge_base import KnowledgeBase

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def create_agent(kb: KnowledgeBase, booking: BookingTools) -> Agent:
    """Create the airline support agent."""
    model = OpenAIChatModel(
        model_name=AGENT_MODEL, settings=ModelSettings(temperature=0.0)
    )  # higher temperature to find stable examples
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
) -> AsyncGenerator[RunEvent, None]:
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
    try:
        async with agent.iter(user_prompt=user_prompt, message_history=original_message_history) as run:
            async for node in run:
                if isinstance(node, CallToolsNode):
                    response = node.model_response
                    if response.finish_reason == "tool_call":
                        text_content = ""
                        for response_part in response.parts:
                            if isinstance(response_part, TextPart):
                                text_content += response_part.content
                            elif isinstance(response_part, ToolCallPart):
                                current_tool_calls[response_part.tool_call_id] = ToolCall(
                                    tool_call_id=response_part.tool_call_id,
                                    tool_name=response_part.tool_name,
                                    arguments=json.dumps(response_part.args),
                                )

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
                    for request_part in request.parts:
                        if isinstance(request_part, ToolReturnPart) and request_part.tool_call_id in current_tool_calls:
                            yield RunEventThreadMessage(
                                id=run_id,
                                object=RunEventObject.THREAD_MESSAGE,
                                data=ToolCallMessage(
                                    thread_id=thread_id,
                                    content=ToolCall(
                                        tool_call_id=request_part.tool_call_id,
                                        tool_name=request_part.tool_name,
                                        arguments=json.dumps(current_tool_calls[request_part.tool_call_id].arguments),
                                        result=request_part.model_response_str(),
                                    ),
                                ),
                            )
                            del current_tool_calls[request_part.tool_call_id]

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
