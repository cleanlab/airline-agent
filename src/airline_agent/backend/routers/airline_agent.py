from collections.abc import AsyncGenerator

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from airline_agent.backend.schemas.message import UserMessage
from airline_agent.backend.services.airline_chat import airline_chat_streaming

router = APIRouter(prefix="/airline-agent")


@router.post("/stream")
async def airline_agent_chat_route(
    message: UserMessage,
    cleanlab_enabled: bool = Query(default=True, description="Whether to enable cleanlab validation"),  # noqa: FBT001
    stream_intermediate_messages: bool = Query(default=False, description="Whether to stream intermediate assistant messages before the final response"),  # noqa: FBT001
) -> StreamingResponse:
    event_generator = airline_chat_streaming(message, cleanlab_enabled, stream_intermediate_messages)

    async def sse_generator() -> AsyncGenerator[str, None]:
        async for event in event_generator:
            yield event.to_sse()

    return StreamingResponse(sse_generator(), media_type="text/event-stream")
