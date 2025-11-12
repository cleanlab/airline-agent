import os
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from airline_agent.backend.schemas.message import UserMessage
from airline_agent.backend.services.airline_chat import airline_chat_streaming
from airline_agent.backend.services.red_teaming_chat import red_teaming_chat_streaming

router = APIRouter(prefix="/agent")


@router.post("/stream")
async def agent_chat_route(
    message: UserMessage,
    cleanlab_enabled: bool = Query(  # noqa: FBT001
        default=True, description="Whether to enable cleanlab validation"
    ),
    stream_intermediate_messages: bool = Query(  # noqa: FBT001
        default=False,
        description="Whether to stream intermediate assistant messages before the final response",
    ),
) -> StreamingResponse:
    match os.getenv("AGENT_MODE"):
        case "red-teaming":
            # hard-code stream_intermediate_messages for red-teaming mode
            event_generator = red_teaming_chat_streaming(message, stream_intermediate_messages=True)
        case _:
            event_generator = airline_chat_streaming(
                message, cleanlab_enabled=cleanlab_enabled, stream_intermediate_messages=stream_intermediate_messages
            )

    async def sse_generator() -> AsyncGenerator[str, None]:
        async for event in event_generator:
            yield event.to_sse()

    return StreamingResponse(sse_generator(), media_type="text/event-stream")
