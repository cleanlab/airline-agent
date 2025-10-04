from __future__ import annotations

import logging
from typing import Any, Optional, cast

from openai.types.chat import ChatCompletionMessageParam, ChatCompletionAssistantMessageParam

from pydantic_ai.messages import ModelResponse, ModelMessage
from pydantic_ai.agent import AgentRunResult

from cleanlab_codex import Project

from airline_agent.cleanlab_utils.conversion_utils import convert_string_to_response_message
from airline_agent.cleanlab_utils.conversion_utils import convert_to_openai_messages
from airline_agent.constants import CONTEXT_RETRIEVAL_TOOLS, FALLBACK_RESPONSE, AGENT_SYSTEM_PROMPT

from codex.types.project_validate_response import ProjectValidateResponse

logger = logging.getLogger(__name__)

def _get_tool_result_as_text(messages: list[ChatCompletionMessageParam], tool_name: str) -> str:
    """
    Extract tool result as text for a specific tool name in the current chat turn.

    Searches through OpenAI ChatCompletion messages to find tool results matching
    the given tool name in the current turn only.

    Args:
        messages: List of OpenAI ChatCompletion conversation messages
        tool_name: Name of the tool to extract results for

    Returns:
        Concatenated text content from matching tool results in current turn
    """
    # 1. Find the last user message (start of current turn)
    last_user_idx = None
    for i in reversed(range(len(messages))):
        if messages[i].get("role") == "user":
            last_user_idx = i
            break

    if last_user_idx is None:
        return ""

    # 2. Find tool call IDs from assistant messages after the last user message
    tool_ids = set()
    for i in range(last_user_idx + 1, len(messages)):
        msg = messages[i]
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            assistant_msg = cast(ChatCompletionAssistantMessageParam, msg)
            for tool_call in assistant_msg["tool_calls"]:
                # Only handle function tool calls, skip custom tool calls
                if tool_call.get("type") == "function":
                    # Type narrow to function tool call
                    func_tool_call = cast(Any, tool_call)  # Use Any to avoid union issues
                    if (
                        func_tool_call.get("function")
                        and func_tool_call["function"].get("name") == tool_name
                        and func_tool_call.get("id")
                    ):
                        tool_ids.add(func_tool_call["id"])

    # 3. Collect content from tool messages in current turn with matching tool_call_ids
    texts = []
    for i in range(last_user_idx + 1, len(messages)):
        msg = messages[i]
        if msg.get("role") == "tool" and msg.get("tool_call_id") in tool_ids:
            content = msg.get("content", "")
            if content:
                texts.append(str(content))

    return "\n\n".join(texts)

def _get_context_as_string(messages: list[ChatCompletionMessageParam]) -> str:
    """Extract context from tool results in the agent's messages."""
    context_parts = ""
    for tool_name in CONTEXT_RETRIEVAL_TOOLS:
        tool_result_text = _get_tool_result_as_text(messages, tool_name)
        if tool_result_text:
            context_parts += f"Context from tool {tool_name}:\n{tool_result_text}\n\n"

    return context_parts

def _get_final_response_message(
    response: ModelResponse, validation_result: ProjectValidateResponse
) -> tuple[ModelResponse, Optional[str]]:
    """
    Determine the final response content based on cleanlab validation results.

    Checks validation results for expert answers or guardrail triggers,
    returning either the original response or a replacement.

    Args:
        results: Validation results from cleanlab
        initial_response: Original model response content
        fallback_response: Fallback text for guardrailed responses

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
    else:
        return response, None

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
        user_input: Latest user input string
        response_str: Latest agent response string
        message_history: Current conversation message history
        thread_id: Optional thread ID for metadata
    Returns:
        Updated message history with validated response
    """
    openai_messages = convert_to_openai_messages(message_history)
    openai_messages.append({"role": "user", "content": query})
    if len(message_history) == 0:  # NOTE: system prompt needs to be added manually if no prior message history
        openai_messages.insert(0, {"role": "system", "content": AGENT_SYSTEM_PROMPT})

    validation_result = project.validate(
        query=query,
        response=result.output,
        messages=openai_messages,
        context=_get_context_as_string(convert_to_openai_messages(result.new_messages())),  # Convert this turns tool calls to text
        metadata={"thread_id": thread_id} if thread_id else None,
    )
    logger.info("[cleanlab] Validation result: %s", validation_result)

    latest_agent_response = result.new_messages()[-1] # TODO: Handle finding latest response smarter
    if isinstance(latest_agent_response, ModelResponse):
        final_response, final_response_str = _get_final_response_message(latest_agent_response, validation_result)
    else:
        msg = "latest agent message is not a ModelResponse"
        raise ValueError(msg)
    
    if final_response_str is not None:
        logger.info("[cleanlab] Response was replaced by cleanlab...")
        user_query = result.new_messages()[0]
        message_history.append(user_query)
        message_history.append(final_response)
        # TODO: Here we would doctor the message history to remove tool calls for the current turn if needed
    else:
        message_history.extend(result.new_messages()) 
        final_response_str = result.output  # No change, use original output

    return message_history, final_response_str