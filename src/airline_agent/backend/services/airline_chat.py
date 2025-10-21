from concurrent.futures import thread
import json
import logging
import pathlib
import uuid
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from pydantic_ai import (
    CallToolsNode,
    ModelMessage,
    ModelRequest,
    ModelRequestNode,
    ModelResponse,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.run import End

from src.airline_agent.agent import create_agent, get_cleanlab_project
from src.airline_agent.cleanlab_utils.validate_utils import (
    get_tools_in_openai_format,
    run_cleanlab_validation_logging_tools,
)
from src.airline_agent.tools.knowledge_base import KnowledgeBase
from src.airline_agent.backend.schemas.message import (
    AgentMessage,
    AssistantMessage,
    MessageRole,
    ToolCall,
    ToolCallMessage,
    UserMessage,
)
from src.airline_agent.backend.schemas.run import Run, RunStatus, RunWithMessageHistory
from src.airline_agent.backend.schemas.run_event import (
    RunEvent,
    RunEventObject,
    RunEventThreadMessage,
    RunEventThreadRunCompleted,
    RunEventThreadRunInProgress,
)

load_dotenv()

logger = logging.getLogger(__name__)

kb = KnowledgeBase(
    kb_path=str(
        pathlib.Path(__file__).parent.parent.parent.parent.parent / "data/kb.json"
    ),
    vector_index_path=str(
        pathlib.Path(__file__).parent.parent.parent.parent.parent / "data/vector-db"
    ),
)
project = get_cleanlab_project()


async def airline_chat_streaming(
    messages: list[AgentMessage], thread_id: str
) -> AsyncGenerator[RunEvent, None]:
    run_id = uuid.uuid4()
    yield RunEventThreadRunInProgress(
        id=run_id,
        object=RunEventObject.THREAD_RUN_IN_PROGRESS,
        data=Run(
            id=run_id,
            status=RunStatus.IN_PROGRESS,
            thread_id=thread_id,
        ),
    )
    agent = create_agent(kb)
    current_tool_calls: dict[str, ToolCall] = {}

    assert len(messages) > 0
    user_prompt = messages[-1].content
    assert isinstance(user_prompt, str)
    message_history = _convert_message_history_to_pydantic_ai_messages(messages[:-1])

    nodes = []
    async with agent.iter(
        user_prompt=user_prompt, message_history=message_history
    ) as run:
        async for node in run:
            nodes.append(node)
            if isinstance(node, CallToolsNode):
                response = node.model_response
                if response.finish_reason == "tool_call":
                    for part in response.parts:
                        if isinstance(part, ToolCallPart):
                            current_tool_calls[part.tool_call_id] = ToolCall(
                                tool_call_id=part.tool_call_id,
                                tool_name=part.tool_name,
                                arguments=json.dumps(part.args),
                            )

            elif isinstance(node, ModelRequestNode) and current_tool_calls:
                request = node.request
                for part in request.parts:
                    if (
                        isinstance(part, ToolReturnPart)
                        and part.tool_call_id in current_tool_calls
                    ):
                        yield RunEventThreadMessage(
                            id=run_id,
                            object=RunEventObject.THREAD_MESSAGE,
                            data=ToolCallMessage(
                                thread_id=thread_id,
                                content=ToolCall(
                                    tool_call_id=part.tool_call_id,
                                    tool_name=part.tool_name,
                                    arguments=json.dumps(
                                        current_tool_calls[part.tool_call_id].arguments
                                    ),
                                    result=part.model_response_str(),
                                ),
                            ),
                        )
                        del current_tool_calls[part.tool_call_id]

            elif isinstance(node, End):
                if run.result is not None:
                    message_history, final_response = (
                        run_cleanlab_validation_logging_tools(
                            project=project,
                            query=user_prompt,
                            result=run.result,
                            message_history=message_history,
                            tools=get_tools_in_openai_format(agent),
                            thread_id=thread_id,
                        )
                    )
                    yield RunEventThreadMessage(
                        id=run_id,
                        object=RunEventObject.THREAD_MESSAGE,
                        data=AssistantMessage(
                            thread_id=thread_id,
                            content=final_response,
                        ),
                    )

    # eval_scores = {
    #     eval_key: EvalResult.model_validate(eval_result.model_dump())
    #     for eval_key, eval_result in response["validation_result"].eval_scores.items()
    # }
    # deterministic_guardrails_results = (
    #     {
    #         guardrail_key: EvalResult(
    #             score=0.0 if guardrail_result.should_guardrail else None,
    #             triggered=guardrail_result.should_guardrail,
    #             triggered_guardrail=guardrail_result.should_guardrail,
    #         )
    #         for guardrail_key, guardrail_result in response[
    #             "validation_result"
    #         ].deterministic_guardrails_results.items()
    #     }
    #     if response["validation_result"].deterministic_guardrails_results is not None
    #     else {}
    # )
    # return Message(
    #     thread_id=thread_id,
    #     role=MessageRole.ASSISTANT,
    #     content=response["response"],
    #     metadata=MessageMetadata(
    #         original_llm_response=response["original_response"],
    #         is_expert_answer=response["validation_result"].expert_answer is not None,
    #         guardrailed=response["validation_result"].should_guardrail,
    #         escalated_to_sme=response["validation_result"].escalated_to_sme,
    #         scores={**eval_scores, **deterministic_guardrails_results},
    #     ),
    # )
    yield RunEventThreadRunCompleted(
        id=run_id,
        object=RunEventObject.THREAD_RUN_COMPLETED,
        data=RunWithMessageHistory(
            id=run_id,
            status=RunStatus.COMPLETED,
            thread_id=thread_id,
            message_history=_convert_pydantic_ai_messages_to_message_history(
                message_history, thread_id
            ),
        ),
    )


def _convert_message_history_to_pydantic_ai_messages(
    messages: list[AgentMessage],
) -> list[ModelMessage]:
    message_history: list[ModelMessage] = []
    for message in messages:
        if message.role == MessageRole.USER:
            assert isinstance(message.content, str)
            message_history.append(
                ModelRequest(parts=[UserPromptPart(content=message.content)])
            )
        elif message.role == MessageRole.ASSISTANT:
            assert isinstance(message.content, str)
            message_history.append(
                ModelResponse(parts=[TextPart(content=message.content)])
            )
        elif message.role == MessageRole.TOOL:
            assert isinstance(message.content, ToolCall)
            message_history.append(
                ModelResponse(
                    parts=[
                        ToolCallPart(
                            tool_call_id=message.content.tool_call_id,
                            tool_name=message.content.tool_name,
                            args=json.loads(message.content.arguments)
                            if message.content.arguments
                            else None,
                        )
                    ]
                )
            )
            message_history.append(
                ModelRequest(
                    parts=[
                        ToolReturnPart(
                            tool_name=message.content.tool_name,
                            tool_call_id=message.content.tool_call_id,
                            content=message.content.result,
                        )
                    ]
                )
            )
    return message_history


def _convert_pydantic_ai_messages_to_message_history(
    messages: list[ModelMessage], thread_id: str
) -> list[AgentMessage]:
    formatted_message_history: list[AgentMessage] = []
    current_tool_calls: dict[str, ToolCall] = {}
    for message in messages:
        if isinstance(message, ModelRequest):
            if len(message.parts) == 0:
                logger.warning("Empty ModelRequest message received")
                continue

            if isinstance(message.parts[0], UserPromptPart):
                content = message.parts[0].content
                for part in message.parts:
                    if isinstance(part, UserPromptPart):
                        content += part.content

                formatted_message_history.append(
                    UserMessage(thread_id=thread_id, content=content).model_dump()
                )
            elif isinstance(message.parts[0], ToolReturnPart):
                for part in message.parts:
                    formatted_message_history.append(
                        ToolCallMessage(
                            thread_id=thread_id,
                            content=ToolCall(
                                tool_call_id=part.tool_call_id,
                                tool_name=part.tool_name,
                                arguments=current_tool_calls[
                                    part.tool_call_id
                                ].arguments,
                                result=part.model_response_str(),
                            ),
                        ).model_dump()
                    )
                    del current_tool_calls[part.tool_call_id]

        elif isinstance(message, ModelResponse):
            if message.finish_reason == "tool_call":
                for part in message.parts:
                    if isinstance(part, ToolCallPart):
                        current_tool_calls[part.tool_call_id] = ToolCall(
                            tool_call_id=part.tool_call_id,
                            tool_name=part.tool_name,
                            arguments=json.dumps(part.args),
                        )
            else:
                content = ""
                for part in message.parts:
                    if isinstance(part, TextPart):
                        content += part.content
                formatted_message_history.append(
                    AssistantMessage(thread_id=thread_id, content=content).model_dump()
                )

    return formatted_message_history
