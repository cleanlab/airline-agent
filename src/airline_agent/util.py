import asyncio
import uuid

from openai.types.chat import ChatCompletionMessageParam

from airline_agent.backend.schemas.message import AssistantMessage, UserMessage
from airline_agent.backend.schemas.run_event import RunEvent, RunEventThreadMessage
from airline_agent.backend.services.airline_chat import airline_chat_streaming, thread_to_messages
from airline_agent.cleanlab_utils.conversion_utils import convert_to_openai_messages


class TestAgent:
    def __init__(self, *, cleanlab_enabled: bool = True) -> None:
        self._thread_id: str = str(uuid.uuid4())
        self._cleanlab_enabled = cleanlab_enabled

    async def _chat_messages_async(self, message: str) -> list[RunEvent]:
        """Internal async method to collect chat events."""
        return [
            event
            async for event in airline_chat_streaming(
                UserMessage(thread_id=self._thread_id, content=message),
                cleanlab_enabled=self._cleanlab_enabled,
                stream_intermediate_messages=False,
            )
        ]

    def chat_messages(self, message: str) -> list[RunEvent]:
        return asyncio.run(self._chat_messages_async(message))

    def chat(self, message: str) -> tuple[str, str | None]:
        events = self.chat_messages(message)
        for event in events[::-1]:
            if isinstance(event, RunEventThreadMessage) and isinstance(event.data, AssistantMessage):
                return event.data.content, event.data.metadata.log_id
        msg = "agent did not return an assistant message"
        raise ValueError(msg)

    async def chat_async(self, message: str) -> tuple[str, str | None]:
        """
        Async version of chat.

        Args:
            message: The message to send

        Returns:
            Tuple of (response, log_id)
        """
        events = await self._chat_messages_async(message)

        for event in events[::-1]:
            if isinstance(event, RunEventThreadMessage) and isinstance(event.data, AssistantMessage):
                return event.data.content, event.data.metadata.log_id

        msg = "agent did not return an assistant message"
        raise ValueError(msg)

    def get_trace(self) -> list[ChatCompletionMessageParam]:
        messages = thread_to_messages[self._thread_id]
        return convert_to_openai_messages(messages)
