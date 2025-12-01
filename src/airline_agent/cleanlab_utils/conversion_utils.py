"""Convert pydantic-ai message history and responses to OpenAI Chat Completions format."""

import base64
from datetime import datetime
from typing import Any, Literal, cast

from openai.types.chat import ChatCompletion, ChatCompletionFunctionToolParam, ChatCompletionMessageParam
from pydantic_ai.messages import (
    AudioUrl,
    BinaryContent,
    BuiltinToolCallPart,
    BuiltinToolReturnPart,
    DocumentUrl,
    ImageUrl,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    RetryPromptPart,
    SystemPromptPart,
    TextPart,
    ThinkingPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
    VideoUrl,
)
from pydantic_ai.tools import ToolDefinition
from pydantic_ai.usage import RequestUsage

from airline_agent.constants import DEMO_DATETIME


def convert_to_openai_messages(message_history: list[ModelMessage]) -> list[ChatCompletionMessageParam]:
    """Convert pydantic-ai message history to OpenAI Chat Completions format."""
    openai_messages: list[dict[str, Any]] = []

    for message in message_history:
        if isinstance(message, ModelRequest):
            # Handle request messages (sent TO the model)
            for part in message.parts:
                if isinstance(part, SystemPromptPart):
                    # Skip SystemPromptPart - handled separately in _get_system_messages()
                    continue
                if isinstance(part, UserPromptPart):
                    openai_messages.append(_convert_user_prompt(part))
                elif isinstance(part, ToolReturnPart):
                    openai_messages.append(
                        {"role": "tool", "tool_call_id": part.tool_call_id, "content": part.model_response_str()}
                    )
                elif isinstance(part, RetryPromptPart):
                    if part.tool_name is None:
                        # Retry as user message
                        openai_messages.append({"role": "user", "content": part.model_response()})
                    else:
                        # Retry as tool message
                        openai_messages.append(
                            {"role": "tool", "tool_call_id": part.tool_call_id, "content": part.model_response()}
                        )
        elif isinstance(message, ModelResponse):
            # Handle response messages (received FROM the model)
            texts: list[str] = []
            tool_calls: list[dict[str, Any]] = []

            for response_part in message.parts:
                if isinstance(response_part, TextPart):
                    texts.append(response_part.content)
                elif isinstance(response_part, ThinkingPart):
                    # Include thinking in <think> tags
                    texts.append(f"<think>\n{response_part.content}\n</think>")
                elif isinstance(response_part, ToolCallPart):
                    tool_calls.append(
                        {
                            "id": response_part.tool_call_id,
                            "type": "function",
                            "function": {
                                "name": response_part.tool_name,
                                "arguments": response_part.args_as_json_str(),
                            },
                        }
                    )
                # Skip built-in tool calls as OpenAI doesn't return them
                elif isinstance(response_part, BuiltinToolCallPart | BuiltinToolReturnPart):
                    pass

            # Create assistant message
            assistant_message: dict[str, Any] = {"role": "assistant"}

            if texts:
                assistant_message["content"] = "\n\n".join(texts)
            else:
                assistant_message["content"] = None

            if tool_calls:
                assistant_message["tool_calls"] = tool_calls

            if message.finish_reason:
                assistant_message["finish_reason"] = message.finish_reason

            openai_messages.append(assistant_message)

    return openai_messages  # type: ignore[return-value]


def _convert_user_prompt(part: UserPromptPart) -> dict[str, Any]:
    """Convert a UserPromptPart to OpenAI format."""
    if isinstance(part.content, str):
        return {"role": "user", "content": part.content}

    content: list[dict[str, Any]] = []

    for item in part.content:
        if isinstance(item, str):
            content.append({"type": "text", "text": item})
        elif isinstance(item, ImageUrl):
            image_content = {"type": "image_url", "image_url": {"url": item.url}}
            # Add detail if specified in vendor_metadata
            if item.vendor_metadata and "detail" in item.vendor_metadata:
                image_url_dict = image_content["image_url"]
                if not isinstance(image_url_dict, dict):
                    msg = "Expected image_url to be a dict"
                    raise TypeError(msg)
                image_url_dict["detail"] = item.vendor_metadata["detail"]
            content.append(image_content)
        elif isinstance(item, BinaryContent):
            if item.is_image:
                # Convert binary image to base64 data URL
                base64_data = base64.b64encode(item.data).decode("utf-8")
                image_content = {
                    "type": "image_url",
                    "image_url": {"url": f"data:{item.media_type};base64,{base64_data}"},
                }
                # Add detail if specified in vendor_metadata
                if item.vendor_metadata and "detail" in item.vendor_metadata:
                    image_url_dict = image_content["image_url"]
                    if not isinstance(image_url_dict, dict):
                        msg = "Expected image_url to be a dict"
                        raise TypeError(msg)
                    image_url_dict["detail"] = item.vendor_metadata["detail"]
                content.append(image_content)
            elif item.is_audio and item.format in ("wav", "mp3"):
                # Handle audio content
                base64_data = base64.b64encode(item.data).decode("utf-8")
                content.append({"type": "input_audio", "input_audio": {"data": base64_data, "format": item.format}})
            elif item.is_document or item.media_type.startswith("text/"):
                # Inline text-like content
                try:
                    text_content = item.data.decode("utf-8")
                    content.append({"type": "text", "text": f"File {item.identifier}:\n{text_content}"})
                except UnicodeDecodeError:
                    # Fall back to binary description
                    content.append(
                        {
                            "type": "text",
                            "text": f"Binary file {item.identifier} ({item.media_type}, {len(item.data)} bytes)",
                        }
                    )
            else:
                # Other binary content - describe it
                content.append(
                    {
                        "type": "text",
                        "text": f"Binary content {item.identifier} ({item.media_type}, {len(item.data)} bytes)",
                    }
                )
        elif isinstance(item, AudioUrl | VideoUrl | DocumentUrl):
            # Handle URL-based media
            if isinstance(item, AudioUrl):
                content.append({"type": "text", "text": f"Audio file: {item.url}"})
            elif isinstance(item, VideoUrl):
                content.append({"type": "text", "text": f"Video file: {item.url}"})
            elif isinstance(item, DocumentUrl):
                content.append({"type": "text", "text": f"Document: {item.url}"})

    return {"role": "user", "content": content}


def convert_tools_to_openai_format(tools: list[ToolDefinition]) -> list[ChatCompletionFunctionToolParam]:
    """Convert pydantic-ai ToolDefinition objects to OpenAI tools format."""
    openai_tools: list[ChatCompletionFunctionToolParam] = []

    for tool in tools:
        function_spec: dict[str, Any] = {
            "name": tool.name,
            "parameters": tool.parameters_json_schema,
        }
        if tool.description:
            function_spec["description"] = tool.description
        if tool.strict is not None:
            function_spec["strict"] = tool.strict

        openai_tool = cast(
            "ChatCompletionFunctionToolParam",
            {
                "type": "function",
                "function": function_spec,
            },
        )
        openai_tools.append(openai_tool)
    return openai_tools


def convert_message_to_chat_completion(message: ChatCompletionMessageParam) -> ChatCompletion:
    """Convert an OpenAI message (like tool call) to a mock OpenAI ChatCompletion object.

    Args:
        message: OpenAI message dict (e.g., assistant message with tool calls)

    Returns:
        Mock OpenAI ChatCompletion object
    """
    # Determine finish_reason from message
    raw_finish_reason = message.get("finish_reason", "tool_calls" if message.get("tool_calls") else "stop")
    # Map 'tool_call' to 'tool_calls' to match ChatCompletion API
    finish_reason = "tool_calls" if raw_finish_reason == "tool_call" else raw_finish_reason

    # Build the message dict for the choice
    choice_message = {
        "content": message.get("content"),
        "refusal": None,
        "role": message.get("role", "assistant"),
        "annotations": [],
        "audio": None,
        "function_call": None,
        "tool_calls": message.get("tool_calls"),
    }

    return cast(
        "ChatCompletion",
        {
            "id": "chatcmpl-mock",
            "choices": [
                {
                    "finish_reason": finish_reason,
                    "index": 0,
                    "logprobs": None,
                    "message": choice_message,
                }
            ],
            "created": int(DEMO_DATETIME.timestamp()),
            "model": "mock-agent",
            "object": "chat.completion",
            "service_tier": "default",
            "system_fingerprint": None,
            "usage": {
                "completion_tokens": 0,
                "prompt_tokens": 0,
                "total_tokens": 0,
                "completion_tokens_details": {
                    "accepted_prediction_tokens": 0,
                    "audio_tokens": 0,
                    "reasoning_tokens": 0,
                    "rejected_prediction_tokens": 0,
                },
                "prompt_tokens_details": {"audio_tokens": 0, "cached_tokens": 0},
            },
        },
    )


def convert_string_to_response_message(
    content: str,
    *,
    timestamp: datetime | None = None,
) -> ModelResponse:
    """Convert an arbitrary string into a pydantic ModelResponse object.

    This is useful for adding external responses (like from other AI systems,
    human responses, or synthetic responses) to the message history.

    Args:
        content: The text content for the response
        timestamp: Optional timestamp, uses current UTC time if not provided

    Returns:
        A ModelResponse object that can be added to message history
    """
    finish_reason: Literal["stop", "length", "content_filter", "tool_call", "error"] = "stop"
    provider_name: str = "cleanlab"
    model_name = None

    if timestamp is None:
        timestamp = DEMO_DATETIME
    text_part = TextPart(content=content)
    usage = RequestUsage(input_tokens=0, output_tokens=0)
    return ModelResponse(
        parts=[text_part],
        usage=usage,
        model_name=model_name,
        timestamp=timestamp,
        provider_name=provider_name,
        finish_reason=finish_reason,
    )
