import json
import logging
import re
import warnings
from typing import Any, cast

from cleanlab_codex import Project
from cleanlab_tlm.utils.chat import _ASSISTANT_PREFIX as ASSISTANT_PREFIX
from cleanlab_tlm.utils.chat import (
    _form_prompt_chat_completions_api as form_prompt_chat_completions_api,
)
from codex.types.project_validate_response import ProjectValidateResponse
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionFunctionToolParam,
    ChatCompletionMessageParam,
)
from pydantic_ai import Agent, ModelSettings
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    TextPart,
    UserPromptPart,
)
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.tools import ToolDefinition

from airline_agent.cleanlab_utils.conversion_utils import (
    convert_message_to_chat_completion,
    convert_string_to_response_message,
    convert_to_openai_messages,
    convert_tools_to_openai_format,
)
from airline_agent.constants import AGENT_MODEL, CONTEXT_RETRIEVAL_TOOLS, FALLBACK_RESPONSE

logger = logging.getLogger(__name__)


def _get_tool_result_as_text(messages: list[ChatCompletionMessageParam], tool_names: list[str]) -> str:
    """
    Extract tool results as text for specified tool names from all messages.

    Searches through OpenAI ChatCompletion messages to find tool results matching
    any of the given tool names from all messages in order.

    Args:
        messages: List of OpenAI ChatCompletion conversation messages
        tool_names: List of tool names to extract results for

    Returns:
        Formatted tool results: "<context from tool: {tool_name}>\n{tool_result_text}\n</context from tool: {tool_name}>" for each result in message order
    """
    # 1. Build mapping of tool call ID to tool name from all assistant messages
    tool_call_to_name = {}
    for msg in messages:
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            assistant_msg = cast("ChatCompletionAssistantMessageParam", msg)
            for tool_call in assistant_msg["tool_calls"]:
                # Only handle function tool calls, skip custom tool calls
                if tool_call.get("type") == "function":
                    # Type narrow to function tool call
                    func_tool_call = cast("Any", tool_call)  # Use Any to avoid union issues
                    if (
                        func_tool_call.get("function")
                        and func_tool_call["function"].get("name") in tool_names
                        and func_tool_call.get("id")
                    ):
                        tool_call_to_name[func_tool_call["id"]] = func_tool_call["function"]["name"]

    # 2. Collect tool results in message order
    results = []
    for msg in messages:
        if msg.get("role") == "tool":
            tool_msg = cast("Any", msg)  # Cast to avoid TypedDict union issues
            if "tool_call_id" in tool_msg and tool_msg["tool_call_id"] in tool_call_to_name:
                content = tool_msg.get("content", "")
                if content:
                    tool_name_for_result = tool_call_to_name[tool_msg["tool_call_id"]]
                results.append(
                    f"<context from tool: {tool_name_for_result}>\n{content}\n</context from tool: {tool_name_for_result}>\n"
                )

    return "\n\n".join(results)


def _get_context_as_string(messages: list[ChatCompletionMessageParam]) -> str:
    """Extract context from tool results in the agent's messages."""
    return _get_tool_result_as_text(messages, CONTEXT_RETRIEVAL_TOOLS)


def _get_latest_agent_response_pydantic(
    messages: list[ModelMessage],
) -> tuple[ModelResponse, int]:
    """Get the latest AI assistant response with stop finish_reason."""
    for i in range(len(messages) - 1, -1, -1):
        message = messages[i]
        if isinstance(message, ModelResponse) and message.finish_reason == "stop":
            return message, i
    msg = "No AI assistant response with 'stop' finish_reason found."
    raise ValueError(msg)


def _get_latest_agent_response_openai(
    openai_messages: list[ChatCompletionMessageParam],
) -> tuple[ChatCompletionMessageParam, int]:
    """Get index of latest AI assistant response with stop finish_reason in OpenAI format."""
    for i in range(len(openai_messages) - 1, -1, -1):
        message = openai_messages[i]
        if message.get("role") == "assistant" and message.get("finish_reason") == "stop":
            return message, i
    msg = "No AI assistant response with 'stop' finish_reason found."
    raise ValueError(msg)


def _get_latest_user_query_message(messages: list[ModelMessage]) -> ModelMessage:
    """Get the latest user query message from the message history."""
    for message in reversed(messages):
        if isinstance(message, ModelRequest):
            for part in message.parts:
                if isinstance(part, UserPromptPart):
                    return message
    msg = "No user query message found in message history"
    raise ValueError(msg)


def _get_final_response_message(
    response: ModelResponse, validation_result: ProjectValidateResponse
) -> tuple[ModelResponse, str | None]:
    """
    Determine the final response content based on cleanlab validation results.

    Checks validation results for expert answers or guardrail triggers,
    returning either the final response and replacement text.

    Args:
        validation_results: Validation results from cleanlab
        response: Original model response content

    Returns:
        Final response as a ModelResponse object and replacement text if applicable
    """
    replacement_text = None
    if validation_result.expert_answer:
        replacement_text = validation_result.expert_answer
    elif validation_result.should_guardrail:
        if validation_result.guardrailed_fallback is not None:
            replacement_text = validation_result.guardrailed_fallback.message
        else:
            replacement_text = FALLBACK_RESPONSE

    if replacement_text:
        return convert_string_to_response_message(replacement_text), replacement_text
    return response, None


def _get_system_messages(
    message_history: list[ModelMessage],
) -> list[ChatCompletionMessageParam]:
    """Get system messages to prepend to validation messages."""
    system_messages: list[ChatCompletionMessageParam] = []
    instructions_added = False
    system_prompts_seen = set()

    for message in message_history:
        if isinstance(message, ModelRequest):
            # Extract instructions and add as system message only once
            if hasattr(message, "instructions") and message.instructions and not instructions_added:
                system_messages.append(
                    cast(
                        "ChatCompletionMessageParam",
                        {"role": "system", "content": message.instructions},
                    )
                )
                instructions_added = True

            # Add SystemPromptPart content from message history
            for part in message.parts:
                if isinstance(part, SystemPromptPart) and part.content not in system_prompts_seen:
                    system_messages.append(
                        cast(
                            "ChatCompletionMessageParam",
                            {"role": "system", "content": part.content},
                        )
                    )
                    system_prompts_seen.add(part.content)

    return system_messages


def _form_response_string_from_message(message: ChatCompletionMessageParam) -> str:
    """Form a response string from a ChatCompletionMessageParam, stripping trailing assistant prefixes."""

    # Suppress the trustworthiness scoring warning from cleanlab_tlm
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*trustworthiness scoring.*")
        response_str = form_prompt_chat_completions_api([message])

    trailing_assistant_prefix_pattern = rf"\s*{ASSISTANT_PREFIX.strip()}\s*$"
    return re.sub(trailing_assistant_prefix_pattern, "", response_str)


def _get_tools_from_agent(agent: Agent) -> list[ToolDefinition]:
    """Get tool definitions from an agent.

    This works for simple agents where tools are defined directly on the agent
    (e.g., via @agent.tool decorators or tools=[...] in constructor).

    Args:
        agent: The pydantic-ai Agent instance

    Returns:
        List of ToolDefinition objects
    """
    tool_definitions = []
    for toolset in agent.toolsets:
        if hasattr(toolset, "tools") and isinstance(toolset.tools, dict):
            tool_definitions.extend([tool.tool_def for tool in toolset.tools.values() if hasattr(tool, "tool_def")])
    return tool_definitions


def get_tools_in_openai_format(agent: Agent) -> list[ChatCompletionFunctionToolParam]:
    """Get tool definitions from an agent in OpenAI ChatCompletion function format."""
    tool_definitions = _get_tools_from_agent(agent)
    return convert_tools_to_openai_format(tool_definitions)


def run_cleanlab_validation(
    project: Project,
    query: str,
    result: AgentRunResult,
    message_history: list[ModelMessage],
    tools: list[ChatCompletionFunctionToolParam] | None = None,
    thread_id: str | None = None,
    additional_metadata: dict[str, Any] | None = None,
) -> tuple[list[ModelMessage], str, ProjectValidateResponse]:
    """
    Run cleanlab validation on the latest agent response and update message history.

    Sends the user input, agent response, and conversation messages to cleanlab
    for validation, then updates the message history with any modifications.

    Args:
        project: Cleanlab Project instance
        query: Latest user input string
        result: Latest agent response
        message_history: Current conversation message history
        tools: Optional list of tools in OpenAI function format for context
        thread_id: Optional thread ID for metadata
        additional_metadata: Optional additional metadata to add to the validation metadata
    Returns:
        Final response as a ModelResponse object and updated message history.
    """
    messages = _get_system_messages(message_history + result.new_messages()) + convert_to_openai_messages(
        message_history
    )
    openai_new_messages = convert_to_openai_messages(result.new_messages())
    latest_agent_response, _ = _get_latest_agent_response_pydantic(result.new_messages())
    _, latest_agent_response_idx_openai = _get_latest_agent_response_openai(openai_new_messages)
    validation_result = project.validate(
        query=query,
        response=result.output,
        messages=messages + openai_new_messages[:latest_agent_response_idx_openai],
        context=_get_context_as_string(openai_new_messages),
        tools=tools,
        metadata=_get_final_metadata(thread_id, additional_metadata),
    )
    logger.info("[cleanlab] Validation result: %s", validation_result)

    final_response_message, final_response_str = _get_final_response_message(latest_agent_response, validation_result)

    if final_response_str is not None:
        logger.info("[cleanlab] Response was replaced by cleanlab...")
        user_query_message = _get_latest_user_query_message(result.new_messages())
        message_history.append(user_query_message)
        message_history.append(final_response_message)
    else:
        message_history.extend(result.new_messages())
        final_response_str = result.output  # No change, use original output

    return message_history, final_response_str, validation_result


def run_cleanlab_validation_logging_tools(
    project: Project,
    query: str,
    result: AgentRunResult,
    message_history: list[ModelMessage],
    tools: list[ChatCompletionFunctionToolParam] | None = None,
    thread_id: str | None = None,
    additional_metadata: dict[str, Any] | None = None,
) -> tuple[list[ModelMessage], str, ProjectValidateResponse]:
    """
    Run cleanlab validation on the latest agent response and update message history.

    Sends the user input, agent response, and conversation messages to cleanlab
    for validation, then updates the message history with any modifications.

    This function logs tool calls into Codex (bypassing validation with perfect scores) before running validation on final output.

    Args:
        project: Cleanlab Project instance
        query: Latest user input string
        result: Latest agent response
        message_history: Current conversation message history
        tools: Optional list of tools in OpenAI function format for context
        thread_id: Optional thread ID for metadata
        additional_metadata: Optional additional metadata to add to the validation metadata
    Returns:
        Final response as a ModelResponse object and updated message history.
    """
    messages = _get_system_messages(message_history + result.new_messages()) + convert_to_openai_messages(
        message_history
    )
    openai_new_messages = convert_to_openai_messages(result.new_messages())

    for index, openai_newest_message in enumerate(
        openai_new_messages
    ):  # Go through new messages and log all assistant calls
        # IMPORTANT: the backend currently relies on this integration LOGGING but BYPASSING VALIDATION for any intermediate AI responses
        # do not change this behavior without updating the backend code
        if openai_newest_message.get("role") == "assistant" and openai_newest_message.get("finish_reason") != "stop":
            openai_response = convert_message_to_chat_completion(openai_newest_message)

            _ = project.validate(
                query=query,
                response=openai_response,
                messages=messages + openai_new_messages[:index],
                context=_get_context_as_string(openai_new_messages),
                tools=tools,
                metadata=_get_final_metadata(thread_id, additional_metadata),
                eval_scores={},
            )
            logger.info("[cleanlab] Logging function call, automatic validation pass.")

    return run_cleanlab_validation(
        project=project,
        query=query,
        result=result,
        message_history=message_history,
        tools=tools,
        thread_id=thread_id,
        additional_metadata=additional_metadata,
    )  # Run real validation on the final output


def _get_final_metadata(thread_id: str | None, additional_metadata: dict[str, Any] | None) -> dict[str, Any] | None:
    """Get the final metadata for the validation."""
    if additional_metadata and thread_id:
        return {"thread_id": thread_id, **additional_metadata}

    if thread_id:
        return {"thread_id": thread_id}

    return None


def validate_tool_call_request(
    project: Project,
    tool_call_id: str,
    tool_name: str,
    tool_arguments: dict[str, Any],
    query: str,
    message_history: list[ModelMessage],
    new_messages: list[ModelMessage],
    tools: list[ChatCompletionFunctionToolParam] | None = None,
    thread_id: str | None = None,
) -> tuple[bool, ProjectValidateResponse | None]:
    """
    Validate a tool call request (assistant's decision to call a tool) using Cleanlab.

    Validates the assistant's tool call decision before the tool is executed.
    Formats the tool call as an assistant message with tool_calls array and validates it.

    Args:
        project: Cleanlab Project instance
        tool_call_id: The ID of the tool call
        tool_name: Name of the tool being called
        tool_arguments: The arguments being passed to the tool
        query: The original user query that led to this tool call
        message_history: Previous conversation message history (before this turn)
        new_messages: New messages from this turn (user query, but NOT the tool call request)
        tools: Optional list of tools in OpenAI function format for context
        thread_id: Optional thread ID for metadata

    Returns:
        Tuple of (is_valid, validation_result)
        - is_valid: True if validation passed (not should_guardrail), False otherwise
        - validation_result: The validation result from Cleanlab, or None if validation failed
    """
    # Format the tool call as an assistant message with tool_calls array
    # This represents the actual structured tool call decision
    tool_call_assistant_message: dict[str, Any] = {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": tool_call_id,
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": json.dumps(tool_arguments) if isinstance(tool_arguments, dict) else str(tool_arguments),
                },
            }
        ],
    }
    
    # Convert the tool call message to a string representation for validation
    # Cleanlab's validate() expects a string response, so we'll format the tool_calls as JSON
    tool_call_response = json.dumps(tool_call_assistant_message["tool_calls"], indent=2)
    
    # Build messages structure consistent with final response validation
    # Include system messages from full history (old + new)
    all_messages = message_history + new_messages
    messages = _get_system_messages(all_messages) + convert_to_openai_messages(message_history)
    
    # Add the new messages (user query) but NOT the tool call request being validated
    openai_new_messages = convert_to_openai_messages(new_messages)
    messages = messages + openai_new_messages
    
    # Add the tool call message to the messages array so Cleanlab sees it as the assistant's response
    # This way Cleanlab can validate the structured tool_calls array
    messages_with_tool_call = messages + [tool_call_assistant_message]
    
    # Get context from new messages only (consistent with final validation)
    context = _get_context_as_string(openai_new_messages)

    # Run validation on the tool call request
    try:
        logger.info(
            "[cleanlab] Calling project.validate() for tool call request: %s (id: %s) with arguments: %s",
            tool_name,
            tool_call_id,
            json.dumps(tool_arguments),
        )
        logger.info(
            "[cleanlab] Tool call response being validated: %s",
            tool_call_response,
        )
        validation_result = project.validate(
            query=query,
            response=tool_call_response,
            messages=messages_with_tool_call,
            context=context,
            tools=tools,
            metadata=_get_final_metadata(thread_id, {"tool_name": tool_name, "tool_arguments": str(tool_arguments), "validation_type": "tool_call_request", "tool_call_id": tool_call_id}),
        )
        logger.info(
            "[cleanlab] Tool call request validation for %s: should_guardrail=%s, log_id=%s",
            tool_name,
            validation_result.should_guardrail,
            validation_result.log_id if hasattr(validation_result, 'log_id') else None,
        )

        # Validation passes if should_guardrail is False
        is_valid = not validation_result.should_guardrail
        return is_valid, validation_result
    except Exception as e:
        logger.exception("[cleanlab] Error validating tool call request for %s: %s", tool_name, e)
        # On error, assume validation failed for safety
        return False, None


def validate_tool_result(
    project: Project,
    tool_name: str,
    tool_result: str,
    tool_arguments: dict[str, Any],
    query: str,
    message_history: list[ModelMessage],
    new_messages: list[ModelMessage],
    tools: list[ChatCompletionFunctionToolParam] | None = None,
    thread_id: str | None = None,
) -> tuple[bool, ProjectValidateResponse | None]:
    """
    Validate a tool call result using Cleanlab.

    Treats the tool result as if it were an assistant response and validates it
    using Cleanlab's validation system. Structures messages consistently with
    final response validation.

    Args:
        project: Cleanlab Project instance
        tool_name: Name of the tool that was called
        tool_result: The tool result as a string (JSON or text)
        tool_arguments: The arguments that were passed to the tool
        query: The original user query that led to this tool call
        message_history: Previous conversation message history (before this turn)
        new_messages: New messages from this turn (user query + tool call request, but NOT the tool return)
        tools: Optional list of tools in OpenAI function format for context
        thread_id: Optional thread ID for metadata

    Returns:
        Tuple of (is_valid, validation_result)
        - is_valid: True if validation passed (not should_guardrail), False otherwise
        - validation_result: The validation result from Cleanlab, or None if validation failed
    """
    # Build messages structure consistent with final response validation
    # Include system messages from full history (old + new)
    all_messages = message_history + new_messages
    messages = _get_system_messages(all_messages) + convert_to_openai_messages(message_history)
    
    # Add the new messages (user query + tool call request) but NOT the tool return being validated
    openai_new_messages = convert_to_openai_messages(new_messages)
    messages = messages + openai_new_messages
    
    # Get context from new messages only (consistent with final validation)
    context = _get_context_as_string(openai_new_messages)

    # Run validation on the tool result
    try:
        # Log what messages are being passed
        logger.info(
            "[cleanlab] Calling project.validate() for tool %s",
            tool_name,
        )
        logger.info(
            "[cleanlab] Query: %s",
            query[:200] if len(query) > 200 else query,
        )
        logger.info(
            "[cleanlab] Response (tool_result) length: %d, preview: %s",
            len(tool_result),
            tool_result[:200] if len(tool_result) > 200 else tool_result,
        )
        logger.info(
            "[cleanlab] Messages count: %d",
            len(messages),
        )
        # Log the structure of messages to see what's included
        for idx, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content_preview = ""
            if "content" in msg and msg["content"]:
                content_str = str(msg["content"])
                content_preview = content_str[:100] if len(content_str) > 100 else content_str
            tool_calls_info = ""
            if "tool_calls" in msg and msg["tool_calls"]:
                tool_calls_info = f", tool_calls: {[tc.get('function', {}).get('name', 'unknown') for tc in msg['tool_calls']]}"
            logger.info(
                "[cleanlab]   Message[%d]: role=%s, content_preview=%s%s",
                idx,
                role,
                content_preview[:100],
                tool_calls_info,
            )
        logger.info(
            "[cleanlab] Context length: %d, preview: %s",
            len(context),
            context[:200] if len(context) > 200 else context,
        )
        
        validation_result = project.validate(
            query=query,
            response=tool_result,
            messages=messages,
            context=context,
            tools=tools,
            metadata=_get_final_metadata(thread_id, {"tool_name": tool_name, "tool_arguments": str(tool_arguments)}),
        )
        logger.info(
            "[cleanlab] Tool result validation for %s: should_guardrail=%s, log_id=%s",
            tool_name,
            validation_result.should_guardrail,
            validation_result.log_id if hasattr(validation_result, 'log_id') else None,
        )

        # Validation passes if should_guardrail is False
        is_valid = not validation_result.should_guardrail
        return is_valid, validation_result
    except Exception as e:
        logger.exception("[cleanlab] Error validating tool result for %s: %s", tool_name, e)
        # On error, assume validation failed for safety
        return False, None


async def generate_tool_fallback_response(
    agent: Agent,
    tool_name: str,
    tool_arguments: dict[str, Any],
    original_query: str,
    message_history: list[ModelMessage],
    validation_result: ProjectValidateResponse,
) -> str:
    """
    Generate a natural fallback response when tool validation fails.

    Uses a separate LLM call with a recovery assistant prompt to generate
    a response that continues the conversation seamlessly without mentioning
    the validation failure.

    Args:
        agent: The main agent (used to extract system prompt)
        tool_name: Name of the tool that failed validation
        tool_arguments: Arguments that were passed to the tool
        original_query: The original user query
        message_history: Current conversation message history
        validation_result: The validation result from Cleanlab

    Returns:
        A JSON string representing the fallback tool result
    """
    # Extract system prompt from agent
    system_prompt = agent.instructions if hasattr(agent, "instructions") else ""

    # Format message history as text
    message_history_text = "\n".join(
        [
            f"{'User' if isinstance(msg, ModelRequest) else 'Assistant'}: {_format_message_for_fallback(msg)}"
            for msg in message_history[-10:]  # Last 10 messages for context
        ]
    )

    # Get trustworthiness score and explanation
    trust_score = None
    trust_explanation = None
    if validation_result.eval_scores and "trustworthiness" in validation_result.eval_scores:
        trust_score_obj = validation_result.eval_scores["trustworthiness"]
        trust_score = trust_score_obj.score if hasattr(trust_score_obj, "score") else None
        if hasattr(trust_score_obj, "log") and trust_score_obj.log:
            trust_explanation = (
                trust_score_obj.log.explanation if hasattr(trust_score_obj.log, "explanation") else None
            )

    # Format the blocked assistant attempt (tool result)
    blocked_attempt = f"Tool '{tool_name}' was called with arguments {json.dumps(tool_arguments)} and returned a result that was flagged as untrustworthy."

    # Build the recovery assistant prompt
    recovery_prompt = f"""You are the Recovery Assistant for the airline support agent.

The previous assistant output was blocked as untrustworthy.

SYSTEM PROMPT:
{system_prompt}

MESSAGE HISTORY:
{message_history_text}

USER MESSAGE:
{original_query}

BLOCKED ASSISTANT ATTEMPT:
{blocked_attempt}

CLEANLAB TRUST INFO:
Score: {trust_score if trust_score is not None else 'N/A'}
Explanation: {trust_explanation if trust_explanation else 'The tool result was flagged as untrustworthy'}

Generate a clear explanation on why you weren't able to help initially with the user's request. Then, provide acorrected response that:
- does NOT mention guardrails, validation, or internal checks
- does NOT retry the blocked tool call or action
- is empathetic, concise, and consistent with airline policy in the system prompt
- guides the user to an appropriate next step

Your response should be a natural continuation of the conversation that helps the user without revealing that a tool call was blocked."""

    # Create a separate agent for fallback generation
    # Use the same model but with a different prompt
    # IMPORTANT: This agent should NOT have any tools or validation hooks
    # We want it to generate a clean fallback without triggering guardrails
    fallback_model = OpenAIChatModel(model_name=AGENT_MODEL, settings=ModelSettings(temperature=0.3))
    # Create agent with NO toolsets to avoid any tool call validation
    fallback_agent = Agent(model=fallback_model, instructions=recovery_prompt, toolsets=[])

    try:
        # Generate the fallback response
        # This should not trigger any validation since it's a separate agent call
        # and we're bypassing the normal airline_chat_streaming flow
        result = await fallback_agent.run(user_prompt=original_query, message_history=[])
        fallback_text = result.output
        
        logger.info(
            "[cleanlab] Fallback generation for tool %s - Generated text: %s",
            tool_name,
            fallback_text,
        )

        # Format as JSON for tool result
        # The fallback should be a JSON object that represents a safe tool result
        # For most tools, we'll return an error-like structure or empty result
        fallback_json = {
            "error": False,
            "message": fallback_text,
            "tool_name": tool_name,
            "note": "This is a fallback response generated when the original tool result was flagged as untrustworthy.",
        }
        
        fallback_json_str = json.dumps(fallback_json)
        logger.info(
            "[cleanlab] Fallback generation for tool %s - Final JSON: %s",
            tool_name,
            fallback_json_str,
        )

        return fallback_json_str
    except Exception as e:
        logger.exception("[cleanlab] Error generating fallback response for tool %s: %s", tool_name, e)
        # Return a default safe fallback
        default_fallback = {
            "error": False,
            "message": FALLBACK_RESPONSE,
            "tool_name": tool_name,
        }
        return json.dumps(default_fallback)


def _format_message_for_fallback(message: ModelMessage) -> str:
    """Format a message for inclusion in fallback prompt."""
    if isinstance(message, ModelRequest):
        for part in message.parts:
            if isinstance(part, UserPromptPart):
                if isinstance(part.content, str):
                    return part.content
                return str(part.content)
    elif isinstance(message, ModelResponse):
        texts = []
        for part in message.parts:
            if isinstance(part, TextPart):
                texts.append(part.content)
        return " ".join(texts)
    return str(message)
