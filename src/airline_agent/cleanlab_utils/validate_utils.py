from __future__ import annotations

import logging
import re
import warnings
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from cleanlab_codex import Project
    from codex.types.project_validate_response import ProjectValidateResponse
    from pydantic_ai.agent import AgentRunResult

from cleanlab_tlm.utils.chat import _ASSISTANT_PREFIX as ASSISTANT_PREFIX
from cleanlab_tlm.utils.chat import _form_prompt_chat_completions_api as form_prompt_chat_completions_api
from openai.types.chat import ChatCompletionAssistantMessageParam, ChatCompletionMessageParam
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, UserPromptPart

from airline_agent.cleanlab_utils.conversion_utils import (
    convert_pydantic_message_history_to_cleanlab_format,
    convert_string_to_response_message,
    convert_to_openai_messages,
)
from airline_agent.constants import (
    AGENT_SYSTEM_PROMPT,
    CONTEXT_RETRIEVAL_TOOLS,
    FALLBACK_RESPONSE,
    get_perfect_eval_scores,
)

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
            assistant_msg = cast(ChatCompletionAssistantMessageParam, msg)
            for tool_call in assistant_msg["tool_calls"]:
                # Only handle function tool calls, skip custom tool calls
                if tool_call.get("type") == "function":
                    # Type narrow to function tool call
                    func_tool_call = cast(Any, tool_call)  # Use Any to avoid union issues
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
            tool_msg = cast(Any, msg)  # Cast to avoid TypedDict union issues
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


def _get_latest_agent_response(messages: list[ModelMessage]) -> tuple[ModelResponse, int]:
    """Get the latest ModelResponse from a list of ModelMessage objects and idx of response."""
    maybe_latest_agent_response = messages[-1]
    if isinstance(maybe_latest_agent_response, ModelResponse):
        return maybe_latest_agent_response, len(messages) - 1
    msg = "Latest message is not a ModelResponse."
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
        replacement_text = FALLBACK_RESPONSE

    if replacement_text:
        return convert_string_to_response_message(replacement_text), replacement_text
    return response, None


def _form_response_string_from_message(message: ChatCompletionMessageParam) -> str:
    """Form a response string from a ChatCompletionMessageParam, stripping trailing assistant prefixes."""

    # Suppress the trustworthiness scoring warning from cleanlab_tlm
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*trustworthiness scoring.*")
        response_str = form_prompt_chat_completions_api([message])

    trailing_assistant_prefix_pattern = rf"\s*{ASSISTANT_PREFIX.strip()}\s*$"
    return re.sub(trailing_assistant_prefix_pattern, "", response_str)


def run_cleanlab_validation(
    project: Project,
    query: str,
    result: AgentRunResult,
    message_history: list[ModelMessage],
    thread_id: str | None = None,
) -> tuple[list[ModelMessage], str]:
    """
    Run cleanlab validation on the latest agent response and update message history.

    Sends the user input, agent response, and conversation messages to cleanlab
    for validation, then updates the message history with any modifications.

    Args:
        project: Cleanlab Project instance
        query: Latest user input string
        result: Latest agent response
        message_history: Current conversation message history
        thread_id: Optional thread ID for metadata
    Returns:
        Final response as a ModelResponse object and updated message history.
    """
    messages = convert_pydantic_message_history_to_cleanlab_format(message_history, query, AGENT_SYSTEM_PROMPT)
    openai_new_messages = convert_to_openai_messages(result.new_messages())
    latest_agent_response, latest_agent_response_idx = _get_latest_agent_response(result.new_messages())

    validation_result = project.validate(
        query=query,
        response=result.output,
        messages=messages + openai_new_messages[:latest_agent_response_idx],
        context=_get_context_as_string(openai_new_messages),
        metadata={"thread_id": thread_id} if thread_id else None,
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

    return message_history, final_response_str


def run_cleanlab_validation_logging_tools(
    project: Project,
    query: str,
    result: AgentRunResult,
    message_history: list[ModelMessage],
    thread_id: str | None = None,
) -> tuple[list[ModelMessage], str]:
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
        thread_id: Optional thread ID for metadata
    Returns:
        Final response as a ModelResponse object and updated message history.
    """
    messages = convert_pydantic_message_history_to_cleanlab_format(message_history, query, AGENT_SYSTEM_PROMPT)
    openai_new_messages = convert_to_openai_messages(result.new_messages())

    for openai_newest_message in openai_new_messages:  # Go through new messages and log all assistant calls
        if openai_newest_message.get("role") == "assistant" and openai_newest_message.get("finish_reason") != "stop":
            response_str = _form_response_string_from_message(openai_newest_message)
            _ = project.validate(
                query=query,
                response=response_str,
                messages=messages,
                context=_get_context_as_string(openai_new_messages),
                metadata={"thread_id": thread_id} if thread_id else None,
                eval_scores=get_perfect_eval_scores(),
            )
            logger.info("[cleanlab] Logging function call, automatic validation pass.")

    return run_cleanlab_validation(
        project=project,
        query=query,
        result=result,
        message_history=message_history,
        thread_id=thread_id,
    )  # Run real validation on the final output
