import json
import logging
import uuid
from collections.abc import AsyncGenerator

from pydantic_ai import (
    CallToolsNode,
    ModelMessage,
    ModelRequestNode,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
)

from airline_agent.backend.schemas.message import (
    AssistantMessage,
    ToolCall,
    ToolCallMessage,
    UserMessage,
)
from airline_agent.backend.schemas.run import Run, RunStatus
from airline_agent.backend.schemas.run_event import (
    RunEvent,
    RunEventObject,
    RunEventThreadMessage,
    RunEventThreadRunCompleted,
    RunEventThreadRunFailed,
    RunEventThreadRunInProgress,
)
from airline_agent.red_teaming.agent import Dependencies, create_agent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

red_teaming_agent = create_agent()

thread_to_messages: dict[str, list[ModelMessage]] = {}


async def red_teaming_chat_streaming(
    message: UserMessage,
    *,
    stream_intermediate_messages: bool,
) -> AsyncGenerator[RunEvent, None]:
    run_id = uuid.uuid4()
    thread_id = message.thread_id

    yield RunEventThreadRunInProgress(
        id=run_id,
        object=RunEventObject.THREAD_RUN_IN_PROGRESS,
        data=Run(
            id=run_id,
            status=RunStatus.IN_PROGRESS,
            thread_id=message.thread_id,
        ),
    )

    if thread_id not in thread_to_messages:
        thread_to_messages[thread_id] = []

    current_tool_calls: dict[str, ToolCall] = {}

    user_prompt = message.content
    message_history = thread_to_messages[thread_id]

    try:
        async with red_teaming_agent.iter(
            user_prompt=user_prompt,
            message_history=message_history,
            deps=Dependencies(thread_id=thread_id),
        ) as run:
            async for node in run:
                if isinstance(node, CallToolsNode):
                    response = node.model_response
                    if response.finish_reason == "tool_call":
                        text_content = ""
                        for response_part in response.parts:
                            if isinstance(response_part, TextPart):
                                text_content += response_part.content
                            elif isinstance(response_part, ToolCallPart):
                                current_tool_calls[response_part.tool_call_id] = ToolCall(
                                    tool_call_id=response_part.tool_call_id,
                                    tool_name=response_part.tool_name,
                                    arguments=json.dumps(response_part.args),
                                )

                        if text_content and stream_intermediate_messages:
                            yield RunEventThreadMessage(
                                id=run_id,
                                object=RunEventObject.THREAD_MESSAGE,
                                data=AssistantMessage(
                                    thread_id=thread_id,
                                    content=text_content,
                                ),
                            )

                elif isinstance(node, ModelRequestNode) and current_tool_calls:
                    request = node.request
                    for request_part in request.parts:
                        if isinstance(request_part, ToolReturnPart) and request_part.tool_call_id in current_tool_calls:
                            yield RunEventThreadMessage(
                                id=run_id,
                                object=RunEventObject.THREAD_MESSAGE,
                                data=ToolCallMessage(
                                    thread_id=thread_id,
                                    content=ToolCall(
                                        tool_call_id=request_part.tool_call_id,
                                        tool_name=request_part.tool_name,
                                        arguments=json.dumps(current_tool_calls[request_part.tool_call_id].arguments),
                                        result=request_part.model_response_str(),
                                    ),
                                ),
                            )
                            del current_tool_calls[request_part.tool_call_id]

            final_response = run.result.output if run.result is not None else ""
            yield RunEventThreadMessage(
                id=run_id,
                object=RunEventObject.THREAD_MESSAGE,
                data=AssistantMessage(
                    thread_id=thread_id,
                    content=final_response,
                ),
            )
            thread_to_messages[thread_id] = run.ctx.state.message_history.copy()

        yield RunEventThreadRunCompleted(
            id=run_id,
            object=RunEventObject.THREAD_RUN_COMPLETED,
            data=Run(
                id=run_id,
                status=RunStatus.COMPLETED,
                thread_id=thread_id,
            ),
        )

    except Exception:
        logger.exception("Error in red-teaming chat streaming")
        yield RunEventThreadRunFailed(
            id=run_id,
            object=RunEventObject.THREAD_RUN_FAILED,
            data=Run(
                id=run_id,
                status=RunStatus.FAILED,
                thread_id=thread_id,
            ),
        )
        raise
