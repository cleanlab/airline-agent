"""Cleanlab Agent that integrates cleanlab validation directly into pydantic-ai."""

from __future__ import annotations

import base64
import logging
import os
import re
import warnings
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast, overload
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator, Sequence

from cleanlab_tlm.utils.chat import _ASSISTANT_PREFIX as ASSISTANT_PREFIX
from cleanlab_tlm.utils.chat import _form_prompt_chat_completions_api as form_prompt_chat_completions_api
from codex import Codex
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionFunctionToolParam,
    ChatCompletionMessageParam,
)
from pydantic_ai.agent.wrapper import WrapperAgent
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
    UserContent,
    UserPromptPart,
    VideoUrl,
)
from pydantic_ai.usage import RequestUsage, RunUsage, UsageLimits
from pydantic_ai.run import AgentRun
from pydantic_ai.settings import ModelSettings
from pydantic_ai.tools import DeferredToolResults
from pydantic_ai.output import OutputSpec
from pydantic_ai import models
from pydantic_ai.toolsets import AbstractToolset
from pydantic_graph import End

# For Python 3.10 compatibility
try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc

# Define type variables
AgentDepsT = TypeVar("AgentDepsT")
OutputDataT = TypeVar("OutputDataT")
RunOutputDataT = TypeVar("RunOutputDataT")

if TYPE_CHECKING:
    from cleanlab_codex import Project
    from codex.types.project_validate_response import ProjectValidateResponse
    from pydantic_ai.agent.abstract import AbstractAgent
    from pydantic_ai.run import AgentRunResult

logger = logging.getLogger(__name__)

# Default values for configurable parameters
DEFAULT_FALLBACK_RESPONSE = "Sorry I am unsure. You can try rephrasing your request."


class CleanlabAgent(WrapperAgent[AgentDepsT, OutputDataT]):
    """Agent wrapper that integrates cleanlab validation into pydantic-ai via iter override."""

    def __init__(
        self,
        wrapped: AbstractAgent[AgentDepsT, OutputDataT],
        cleanlab_project: Project,
        *,
        context_retrieval_tools: list[str] | None = None,
        fallback_response: str = DEFAULT_FALLBACK_RESPONSE,
        thread_id: str | None = None,
        codex_api_key: str | None = None,
    ) -> None:
        """Initialize the Cleanlab agent wrapper.

        Args:
            wrapped: The original pydantic-ai Agent to wrap
            cleanlab_project: Cleanlab Project instance for validation
            context_retrieval_tools: List of tool names to extract context from. Defaults to empty list.
            fallback_response: Response to use when cleanlab triggers guardrail. 
                Defaults to "Sorry I am unsure. You can try rephrasing your request."
            thread_id: Optional thread ID for validation metadata
            codex_api_key: Optional Codex API key, will try CODEX_API_KEY env var if not provided
        """
        super().__init__(wrapped)
        self.cleanlab_project = cleanlab_project
        self.context_retrieval_tools = context_retrieval_tools or []
        self.fallback_response = fallback_response
        self.thread_id = thread_id
        self.openai_tools = self._extract_tools_to_openai_format()
        self.codex_api_key = os.getenv("CODEX_API_KEY", None) or codex_api_key
        if not self.codex_api_key:
            logger.error("CODEX_API_KEY environment variable is not set.")

        self.perfect_eval_scores = self._get_perfect_eval_scores()

    def _extract_tools_to_openai_format(self) -> list[ChatCompletionFunctionToolParam]:
        """Extract tools from the wrapped agent and convert to OpenAI format."""
        tool_definitions = [
            tool.tool_def
            for toolset in self.wrapped.toolsets
            if hasattr(toolset, "tools") and isinstance(toolset.tools, dict)
            for tool in toolset.tools.values()
            if hasattr(tool, "tool_def")
        ]

        openai_tools: list[ChatCompletionFunctionToolParam] = []
        for tool in tool_definitions:
            function_spec: dict[str, Any] = {
                "name": tool.name,
                "parameters": tool.parameters_json_schema,
            }
            if tool.description:
                function_spec["description"] = tool.description
            if tool.strict is not None:
                function_spec["strict"] = tool.strict

            openai_tool = cast(
                ChatCompletionFunctionToolParam,
                {
                    "type": "function",
                    "function": function_spec,
                },
            )
            openai_tools.append(openai_tool)

        return openai_tools

    def _extract_user_query(
        self,
        user_prompt: str | Sequence[UserContent] | None,
        message_history: list[ModelMessage] | None = None,
    ) -> str:
        """Extract the user query string from the run parameters."""
        if isinstance(user_prompt, str):
            return user_prompt

        if user_prompt is not None:
            # Handle multimodal content - extract text parts
            text_parts = [content for content in user_prompt if isinstance(content, str)]
            return " ".join(text_parts)

        if message_history:
            # Extract from latest user message in history
            for message in reversed(message_history):
                if isinstance(message, ModelRequest):
                    for part in message.parts:
                        if isinstance(part, UserPromptPart):
                            if isinstance(part.content, str):
                                return part.content
                            # Handle multimodal content
                            text_parts = [item for item in part.content if isinstance(item, str)]
                            return " ".join(text_parts)
        return ""

    def _convert_to_openai_messages(self, message_history: list[ModelMessage]) -> list[ChatCompletionMessageParam]:
        """Convert pydantic-ai message history to OpenAI Chat Completions format."""
        openai_messages: list[dict[str, Any]] = []
        instructions_added = False

        for message in message_history:
            if isinstance(message, ModelRequest):
                # Handle request messages (sent TO the model)
                # Extract instructions and add as system message only once at the start
                if hasattr(message, "instructions") and message.instructions and not instructions_added:
                    openai_messages.append({"role": "system", "content": message.instructions})
                    instructions_added = True

                for part in message.parts:
                    if isinstance(part, SystemPromptPart):
                        openai_messages.append({"role": "system", "content": part.content})
                    elif isinstance(part, UserPromptPart):
                        openai_messages.append(self._convert_user_prompt(part))
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

    def _convert_user_prompt(self, part: UserPromptPart) -> dict[str, Any]:
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

    def _convert_message_to_chat_completion(self, message: ChatCompletionMessageParam) -> ChatCompletion:
        """Convert an OpenAI message (like tool call) to a mock OpenAI ChatCompletion object."""
        raw_finish_reason = message.get("finish_reason", "tool_calls" if message.get("tool_calls") else "stop")
        finish_reason = "tool_calls" if raw_finish_reason == "tool_call" else raw_finish_reason

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
            ChatCompletion,
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
                "created": int(datetime.now(UTC).timestamp()),
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

    def _convert_string_to_response_message(
        self,
        content: str,
        *,
        timestamp: datetime | None = None,
    ) -> ModelResponse:
        """Convert an arbitrary string into a pydantic ModelResponse object."""
        finish_reason: Literal["stop", "length", "content_filter", "tool_call", "error"] = "stop"
        provider_name: str = "cleanlab"
        model_name = None

        if timestamp is None:
            timestamp = datetime.now(UTC)
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

    def _get_perfect_eval_scores(self) -> dict[str, float]:
        """Get perfect eval scores, cached after first call."""
        client = Codex(api_key=self.codex_api_key)
        project = client.projects.retrieve(self.cleanlab_project.id)
        eval_config = project.config.eval_config

        if not eval_config:
            logger.warning("No eval_config found in project")
            return {
                "trustworthiness": 1.0,
                "response_helpfulness": 1.0,
                "context_sufficiency": 1.0,
                "response_groundedness": 1.0,
                "query_ease": 1.0,
            }

        eval_keys = []

        # Add default evals if they exist
        if eval_config.default_evals:
            default_evals_dump = eval_config.default_evals.model_dump()
            if default_evals_dump:
                eval_keys.extend([evaluation["eval_key"] for evaluation in default_evals_dump.values()])

        # Add custom evals if they exist
        if eval_config.custom_evals and eval_config.custom_evals.evals:
            eval_keys.extend([evaluation.eval_key for evaluation in eval_config.custom_evals.evals.values()])

        logger.info("Retrieved evals: %s", eval_keys)
        return {eval_key: 1.0 for eval_key in eval_keys}

    def _get_tool_result_as_text(self, messages: list[ChatCompletionMessageParam], tool_names: list[str]) -> str:
        """Extract tool results as text for specified tool names from all messages."""
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

    def _get_context_as_string(self, messages: list[ChatCompletionMessageParam]) -> str:
        """Extract context from tool results in the agent's messages."""
        return self._get_tool_result_as_text(messages, self.context_retrieval_tools)

    def _get_latest_agent_response_pydantic(self, messages: list[ModelMessage]) -> tuple[ModelResponse, int]:
        """Get the latest AI assistant response with stop finish_reason."""
        for i in range(len(messages) - 1, -1, -1):
            message = messages[i]
            if isinstance(message, ModelResponse) and message.finish_reason == "stop":
                return message, i
        msg = "No AI assistant response with 'stop' finish_reason found."
        raise ValueError(msg)

    def _get_latest_agent_response_openai(
        self, openai_messages: list[ChatCompletionMessageParam]
    ) -> tuple[ChatCompletionMessageParam, int]:
        """Get index of latest AI assistant response with stop finish_reason in OpenAI format."""
        for i in range(len(openai_messages) - 1, -1, -1):
            message = openai_messages[i]
            if message.get("role") == "assistant" and message.get("finish_reason") == "stop":
                return message, i
        msg = "No AI assistant response with 'stop' finish_reason found."
        raise ValueError(msg)

    def _get_latest_user_query_message(self, messages: list[ModelMessage]) -> ModelMessage:
        """Get the latest user query message from the message history."""
        for message in reversed(messages):
            if isinstance(message, ModelRequest):
                for part in message.parts:
                    if isinstance(part, UserPromptPart):
                        return message
        msg = "No user query message found in message history"
        raise ValueError(msg)

    def _get_final_response_message(
        self, response: ModelResponse, validation_result: ProjectValidateResponse
    ) -> tuple[ModelResponse, str | None]:
        """Determine the final response content based on cleanlab validation results."""
        replacement_text = None
        if validation_result.expert_answer:
            replacement_text = validation_result.expert_answer
        elif validation_result.should_guardrail:
            replacement_text = self.fallback_response

        if replacement_text:
            return self._convert_string_to_response_message(replacement_text), replacement_text
        return response, None

    def _form_response_string_from_message(self, message: ChatCompletionMessageParam) -> str:
        """Form a response string from a ChatCompletionMessageParam, stripping trailing assistant prefixes."""
        # Suppress the trustworthiness scoring warning from cleanlab_tlm
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=".*trustworthiness scoring.*")
            response_str = form_prompt_chat_completions_api([message])

        trailing_assistant_prefix_pattern = rf"\s*{ASSISTANT_PREFIX.strip()}\s*$"
        return re.sub(trailing_assistant_prefix_pattern, "", response_str)

    def _run_cleanlab_validation_logging_tools(
        self,
        project: Project,
        query: str,
        result: AgentRunResult,
        message_history: list[ModelMessage],
        tools: list[ChatCompletionFunctionToolParam] | None = None,
        thread_id: str | None = None,
    ) -> tuple[list[ModelMessage], str]:
        """Run cleanlab validation with tool call logging."""
        messages = self._convert_to_openai_messages(message_history)
        openai_new_messages = self._convert_to_openai_messages(result.new_messages())

        for index, openai_newest_message in enumerate(openai_new_messages):
            if (
                openai_newest_message.get("role") == "assistant"
                and openai_newest_message.get("finish_reason") != "stop"
            ):
                openai_response = self._convert_message_to_chat_completion(openai_newest_message)

                _ = project.validate(
                    query=query,
                    response=openai_response,
                    messages=messages + openai_new_messages[:index],
                    context=self._get_context_as_string(openai_new_messages),
                    tools=tools,
                    metadata={"thread_id": thread_id} if thread_id else None,
                    eval_scores=self.perfect_eval_scores,
                )
                logger.info("[cleanlab] Logging function call, automatic validation pass.")

        return self._run_cleanlab_validation(
            project=project,
            query=query,
            result=result,
            message_history=message_history,
            tools=tools,
            thread_id=thread_id,
        )

    def _run_cleanlab_validation(
        self,
        project: Project,
        query: str,
        result: AgentRunResult,
        message_history: list[ModelMessage],
        tools: list[ChatCompletionFunctionToolParam] | None = None,
        thread_id: str | None = None,
    ) -> tuple[list[ModelMessage], str]:
        """Run cleanlab validation on the latest agent response and update message history."""
        messages = self._convert_to_openai_messages(message_history)
        openai_new_messages = self._convert_to_openai_messages(result.new_messages())
        _, latest_agent_response_idx_openai = self._get_latest_agent_response_openai(openai_new_messages)

        validation_result = project.validate(
            query=query,
            response=result.output,
            messages=messages + openai_new_messages[:latest_agent_response_idx_openai],
            context=self._get_context_as_string(openai_new_messages),
            tools=tools,
            metadata={"thread_id": thread_id} if thread_id else None,
        )
        logger.info("[cleanlab] Validation result: %s", validation_result)

        latest_agent_response, _ = self._get_latest_agent_response_pydantic(result.new_messages())
        final_response_message, final_response_str = self._get_final_response_message(
            latest_agent_response, validation_result
        )
        print("FINAL RESPONSE MESSAGE!!!", final_response_message)
        if final_response_str is not None:
            logger.info("[cleanlab] Response was replaced by cleanlab...")
            user_query_message = self._get_latest_user_query_message(result.new_messages())
            message_history.append(user_query_message)
            message_history.append(final_response_message)
        else:
            message_history.extend(result.new_messages())
            final_response_str = result.output

        return message_history, final_response_str

    @overload
    def iter(
        self,
        user_prompt: str | Sequence[UserContent] | None = None,
        *,
        output_type: None = None,
        message_history: list[ModelMessage] | None = None,
        deferred_tool_results: DeferredToolResults | None = None,
        model: models.Model | models.KnownModelName | str | None = None,
        deps: AgentDepsT = None,
        model_settings: ModelSettings | None = None,
        usage_limits: UsageLimits | None = None,
        usage: RunUsage | None = None,
        infer_name: bool = True,
        toolsets: Sequence[AbstractToolset[AgentDepsT]] | None = None,
    ) -> "AgentRun[AgentDepsT, OutputDataT]": ...

    @overload
    def iter(
        self,
        user_prompt: str | Sequence[UserContent] | None = None,
        *,
        output_type: OutputSpec[RunOutputDataT],
        message_history: list[ModelMessage] | None = None,
        deferred_tool_results: DeferredToolResults | None = None,
        model: models.Model | models.KnownModelName | str | None = None,
        deps: AgentDepsT = None,
        model_settings: ModelSettings | None = None,
        usage_limits: UsageLimits | None = None,
        usage: RunUsage | None = None,
        infer_name: bool = True,
        toolsets: Sequence[AbstractToolset[AgentDepsT]] | None = None,
    ) -> "AgentRun[AgentDepsT, RunOutputDataT]": ...

    @asynccontextmanager
    async def iter(
        self,
        user_prompt: str | Sequence[UserContent] | None = None,
        *,
        output_type: OutputSpec[RunOutputDataT] | None = None,
        message_history: list[ModelMessage] | None = None,
        deferred_tool_results: DeferredToolResults | None = None,
        model: models.Model | models.KnownModelName | str | None = None,
        deps: AgentDepsT = None,
        model_settings: ModelSettings | None = None,
        usage_limits: UsageLimits | None = None,
        usage: RunUsage | None = None,
        infer_name: bool = True,
        toolsets: Sequence[AbstractToolset[AgentDepsT]] | None = None,
    ) -> AsyncIterator[AgentRun[AgentDepsT, Any]]:
        """A contextmanager which can be used to iterate over the agent graph's nodes with Cleanlab validation.

        This method builds an internal agent graph (using system prompts, tools and output schemas) and then returns an
        `AgentRun` object. The `AgentRun` can be used to async-iterate over the nodes of the graph as they are
        executed. When the agent completes and produces a final result, Cleanlab validation is applied.

        Args:
            user_prompt: User input to start/continue the conversation.
            output_type: Custom output type to use for this run.
            message_history: History of the conversation so far.
            deferred_tool_results: Optional results for deferred tool calls in the message history.
            model: Optional model to use for this run, required if `model` was not set when creating the agent.
            deps: Optional dependencies to use for this run.
            model_settings: Optional settings to use for this model's request.
            usage_limits: Optional limits on model request count or token usage.
            usage: Optional usage to start with, useful for resuming a conversation or agents used in tools.
            infer_name: Whether to try to infer the agent name from the call frame if it's not set.
            toolsets: Optional additional toolsets for this run.

        Returns:
            An `AgentRun` object that can be async-iterated over.
        """
        user_query = self._extract_user_query(user_prompt, message_history)

        # Start the wrapped agent's iteration
        async with self.wrapped.iter(
            user_prompt=user_prompt,
            output_type=output_type,
            message_history=message_history,
            deferred_tool_results=deferred_tool_results,
            model=model,
            deps=deps,
            model_settings=model_settings,
            usage_limits=usage_limits,
            usage=usage,
            infer_name=infer_name,
            toolsets=toolsets,
        ) as agent_run:
            # Track if we've handled the final result
            handled_final_result = False
            original_result = None

            # Create a wrapper that intercepts the final result
            class CleanlabAgentRun:
                def __init__(self, wrapped_run: AgentRun, cleanlab_agent: CleanlabAgent):
                    self._wrapped = wrapped_run
                    self._cleanlab_agent = cleanlab_agent
                    self._modified_result = None

                def __getattr__(self, name):
                    """Delegate all other attributes to the wrapped agent run."""
                    return getattr(self._wrapped, name)
                
                @property
                def result(self):
                    """Override result property to return modified result if available."""
                    if self._modified_result is not None:
                        return self._modified_result
                    return self._wrapped.result

                async def __anext__(self):
                    """Override async iteration to intercept End nodes."""
                    nonlocal handled_final_result, original_result
                    
                    node = await self._wrapped.__anext__()
                    
                    # If this is an End node and we haven't handled the final result yet
                    if isinstance(node, End) and not handled_final_result:
                        handled_final_result = True
                        original_result = self._wrapped.result
                        
                        if original_result:
                            logger.info("[cleanlab] Running validation and cleanup...")
                            current_history = list(message_history) if message_history else []

                            updated_history, final_response_str = self._cleanlab_agent._run_cleanlab_validation_logging_tools(
                                project=self._cleanlab_agent.cleanlab_project,
                                query=user_query,
                                result=original_result,
                                message_history=current_history,
                                tools=self._cleanlab_agent.openai_tools,
                                thread_id=self._cleanlab_agent.thread_id,
                            )

                            # Update the wrapped run's state with validated results
                            if hasattr(self._wrapped, '_graph_run') and hasattr(self._wrapped._graph_run, 'state'):
                                # Update message history in the graph state
                                self._wrapped._graph_run.state.message_history = updated_history
                                logger.info("[cleanlab] Updated agent run's internal message history: %d messages", len(updated_history))

                            # If the response was changed, create a modified result
                            print("ORIGINAL RESULT", original_result)
                            print("OUTPUT", original_result.output)
                            print("FINAL RESPONSE STR", final_response_str)
                            if final_response_str != original_result.output:
                                logger.info("[cleanlab] Response was modified by validation - creating new result")
                                
                                # Create a copy of the original result with the new output
                                from pydantic_ai.run import AgentRunResult
                                self._modified_result = AgentRunResult(
                                    output=final_response_str,
                                    output_tool_name=original_result._output_tool_name,
                                    state=original_result._state,
                                    new_message_index=original_result._new_message_index,
                                    traceparent=original_result._traceparent,
                                )
                                logger.info("[cleanlab] Updated AgentRun result with corrected output")

                    return node

                def __aiter__(self):
                    return self

            # Yield the wrapped agent run
            yield CleanlabAgentRun(agent_run, self)

    def get_tools_openai_format(self) -> list[ChatCompletionFunctionToolParam]:
        """Get the agent's tools in OpenAI format."""
        return self.openai_tools