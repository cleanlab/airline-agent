"""Convert pydantic-ai message history and responses to OpenAI Chat Completions format."""

from __future__ import annotations

import base64
import argparse

from typing import Any, Dict, List, Literal

from openai.types.chat import ChatCompletionMessageParam

from pydantic_ai.usage import RequestUsage
from datetime import datetime, timezone

from pydantic_ai.messages import (
    BinaryContent,
    BuiltinToolCallPart,
    BuiltinToolReturnPart,
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
    AudioUrl,
    DocumentUrl,
)

def str_to_bool(v: str) -> bool:
    """Convert string to boolean for argparse."""
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
    
def convert_to_openai_messages(message_history: List[ModelMessage]) -> List[ChatCompletionMessageParam]:
    """Convert pydantic-ai message history to OpenAI Chat Completions format.
    
    Args:
        message_history: List of ModelMessage objects from pydantic-ai
        
    Returns:
        List of OpenAI ChatCompletionMessageParam objects
    """
    openai_messages: List[dict[str, Any]] = []

    for message in message_history:
        if isinstance(message, ModelRequest):
            # Handle request messages (sent TO the model)
            for part in message.parts:
                if isinstance(part, SystemPromptPart):
                    openai_messages.append({
                        'role': 'system',
                        'content': part.content
                    })
                elif isinstance(part, UserPromptPart):
                    openai_messages.append(_convert_user_prompt(part))
                elif isinstance(part, ToolReturnPart):
                    openai_messages.append({
                        'role': 'tool',
                        'tool_call_id': part.tool_call_id,
                        'content': part.model_response_str()
                    })
                elif isinstance(part, RetryPromptPart):
                    if part.tool_name is None:
                        # Retry as user message
                        openai_messages.append({
                            'role': 'user',
                            'content': part.model_response()
                        })
                    else:
                        # Retry as tool message
                        openai_messages.append({
                            'role': 'tool',
                            'tool_call_id': part.tool_call_id,
                            'content': part.model_response()
                        })
        elif isinstance(message, ModelResponse):
            # Handle response messages (received FROM the model)
            texts: List[str] = []
            tool_calls: List[Dict[str, Any]] = []
            
            for response_part in message.parts:  # Changed from 'part' to 'response_part'
                if isinstance(response_part, TextPart):
                    texts.append(response_part.content)
                elif isinstance(response_part, ThinkingPart):
                    # Include thinking in <think> tags
                    texts.append(f"<think>\n{response_part.content}\n</think>")
                elif isinstance(response_part, ToolCallPart):
                    tool_calls.append({
                        'id': response_part.tool_call_id,
                        'type': 'function',
                        'function': {
                            'name': response_part.tool_name,
                            'arguments': response_part.args_as_json_str()
                        }
                    })
                # Skip built-in tool calls as OpenAI doesn't return them
                elif isinstance(response_part, (BuiltinToolCallPart, BuiltinToolReturnPart)):
                    pass
            
            # Create assistant message
            assistant_message: dict[str, Any] = {'role': 'assistant'}

            if texts:
                assistant_message['content'] = '\n\n'.join(texts)
            else:
                assistant_message['content'] = None
                
            if tool_calls:
                assistant_message['tool_calls'] = tool_calls
                
            openai_messages.append(assistant_message)
    
    # Return the messages - they're already compatible with ChatCompletionMessageParam
    return openai_messages  # type: ignore[return-value]


def _convert_user_prompt(part: UserPromptPart) -> dict[str, Any]:
    """Convert a UserPromptPart to OpenAI format."""
    if isinstance(part.content, str):
        return {
            'role': 'user',
            'content': part.content
        }
    
    # Handle multimodal content
    content: List[Dict[str, Any]] = []
    
    for item in part.content:
        if isinstance(item, str):
            content.append({
                'type': 'text',
                'text': item
            })
        elif isinstance(item, ImageUrl):
            image_content = {
                'type': 'image_url',
                'image_url': {'url': item.url}
            }
            # Add detail if specified in vendor_metadata
            if item.vendor_metadata and 'detail' in item.vendor_metadata:
                image_url_dict = image_content['image_url']
                assert isinstance(image_url_dict, dict)
                image_url_dict['detail'] = item.vendor_metadata['detail']
            content.append(image_content)
        elif isinstance(item, BinaryContent):
            if item.is_image:
                # Convert binary image to base64 data URL
                base64_data = base64.b64encode(item.data).decode('utf-8')
                image_content = {
                    'type': 'image_url',
                    'image_url': {
                        'url': f'data:{item.media_type};base64,{base64_data}'
                    }
                }
                # Add detail if specified in vendor_metadata
                if item.vendor_metadata and 'detail' in item.vendor_metadata:
                    image_url_dict = image_content['image_url']
                    assert isinstance(image_url_dict, dict)
                    image_url_dict['detail'] = item.vendor_metadata['detail']
                content.append(image_content)
            elif item.is_audio and item.format in ('wav', 'mp3'):
                # Handle audio content
                base64_data = base64.b64encode(item.data).decode('utf-8')
                content.append({
                    'type': 'input_audio',
                    'input_audio': {
                        'data': base64_data,
                        'format': item.format
                    }
                })
            elif item.is_document or item.media_type.startswith('text/'):
                # Inline text-like content
                try:
                    text_content = item.data.decode('utf-8')
                    content.append({
                        'type': 'text',
                        'text': f'File {item.identifier}:\n{text_content}'
                    })
                except UnicodeDecodeError:
                    # Fall back to binary description
                    content.append({
                        'type': 'text',
                        'text': f'Binary file {item.identifier} ({item.media_type}, {len(item.data)} bytes)'
                    })
            else:
                # Other binary content - describe it
                content.append({
                    'type': 'text',
                    'text': f'Binary content {item.identifier} ({item.media_type}, {len(item.data)} bytes)'
                })
        elif isinstance(item, (AudioUrl, VideoUrl, DocumentUrl)):
            # Handle URL-based media
            if isinstance(item, AudioUrl):
                content.append({
                    'type': 'text',
                    'text': f'Audio file: {item.url}'
                })
            elif isinstance(item, VideoUrl):
                content.append({
                    'type': 'text',
                    'text': f'Video file: {item.url}'
                })
            elif isinstance(item, DocumentUrl):
                content.append({
                    'type': 'text',
                    'text': f'Document: {item.url}'
                })
    
    return {
        'role': 'user',
        'content': content
    }


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
    finish_reason: Literal['stop', 'length', 'content_filter', 'tool_call', 'error'] = "stop"
    provider_name: str = "cleanlab"
    model_name = None

    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    text_part = TextPart(content=content)
    usage = RequestUsage(
        input_tokens=0,
        output_tokens=0
    )
    return ModelResponse(
        parts=[text_part],
        usage=usage,
        model_name=model_name,
        timestamp=timestamp,
        provider_name=provider_name,
        finish_reason=finish_reason
    )