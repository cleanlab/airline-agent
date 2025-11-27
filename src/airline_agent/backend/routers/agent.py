import os
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from airline_agent.backend.schemas.message import UserMessage
from airline_agent.backend.services.airline_chat import airline_chat_streaming
from airline_agent.backend.services.red_teaming_chat import red_teaming_chat_streaming

router = APIRouter(prefix="/agent")


@router.post("/stream")
async def agent_chat_route(
    message: UserMessage,
    *,
    cleanlab_enabled: Annotated[bool, Query(description="Whether to enable cleanlab validation")] = True,
    stream_intermediate_messages: Annotated[
        bool,
        Query(description="Whether to stream intermediate assistant messages before the final response"),
    ] = False,
) -> StreamingResponse:
    match os.getenv("AGENT_MODE"):
        case "red-teaming":
            # hard-code stream_intermediate_messages for red-teaming mode
            event_generator = red_teaming_chat_streaming(message, stream_intermediate_messages=True)
        case _:
            event_generator = airline_chat_streaming(
                message, cleanlab_enabled=cleanlab_enabled, stream_intermediate_messages=stream_intermediate_messages
            )

    async def sse_generator() -> AsyncGenerator[str]:
        async for event in event_generator:
            yield event.to_sse()

    return StreamingResponse(sse_generator(), media_type="text/event-stream")
