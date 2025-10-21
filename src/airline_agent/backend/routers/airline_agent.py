from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.airline_agent.backend.schemas.message import UserMessage
from src.airline_agent.backend.services.airline_chat import airline_chat_streaming

router = APIRouter(prefix="/airline-agent")


@router.post("/stream")
async def airline_agent_chat_route(
    message: UserMessage,
) -> StreamingResponse:
    event_generator = airline_chat_streaming(message)

    async def sse_generator() -> AsyncGenerator[str, None]:
        async for event in event_generator:
            yield event.to_sse()

    return StreamingResponse(sse_generator(), media_type="text/event-stream")
