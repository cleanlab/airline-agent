import json
import logging
import pathlib
import uuid
from collections.abc import AsyncGenerator

from codex.types import ProjectValidateResponse
from dotenv import load_dotenv
from pydantic_ai import (
    CallToolsNode,
    ModelMessage,
    ModelRequestNode,
    ToolCallPart,
    ToolReturnPart,
)

from airline_agent.agent import create_agent, get_cleanlab_project
from airline_agent.backend.schemas.message import (
    AssistantMessage,
    EvalResult,
    MessageMetadata,
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
from airline_agent.cleanlab_utils.validate_utils import (
    get_tools_in_openai_format,
    run_cleanlab_validation_logging_tools,
)
from airline_agent.tools.knowledge_base import KnowledgeBase

load_dotenv()

logger = logging.getLogger(__name__)

kb = KnowledgeBase(
    kb_path=str(pathlib.Path(__file__).parent.parent.parent.parent.parent / "data/kb.json"),
    vector_index_path=str(pathlib.Path(__file__).parent.parent.parent.parent.parent / "data/vector-db"),
)
project = get_cleanlab_project()
agent = create_agent(kb)

thread_to_messages: dict[str, list[ModelMessage]] = {}


async def airline_chat_streaming(
    message: UserMessage,
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

    nodes = []
    original_message_history = thread_to_messages[thread_id].copy()
    try:
        async with agent.iter(user_prompt=user_prompt, message_history=original_message_history) as run:
            async for node in run:
                nodes.append(node)
                if isinstance(node, CallToolsNode):
                    response = node.model_response
                    if response.finish_reason == "tool_call":
                        for response_part in response.parts:
                            if isinstance(response_part, ToolCallPart):
                                current_tool_calls[response_part.tool_call_id] = ToolCall(
                                    tool_call_id=response_part.tool_call_id,
                                    tool_name=response_part.tool_name,
                                    arguments=json.dumps(response_part.args),
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

            if run.result is not None:
                updated_message_history, final_response, validation_result = run_cleanlab_validation_logging_tools(
                    project=project,
                    query=user_prompt,
                    result=run.result,
                    message_history=original_message_history,
                    tools=get_tools_in_openai_format(agent),
                    thread_id=thread_id,
                )
                yield RunEventThreadMessage(
                    id=run_id,
                    object=RunEventObject.THREAD_MESSAGE,
                    data=AssistantMessage(
                        thread_id=thread_id,
                        content=final_response,
                        metadata=MessageMetadata(
                            original_llm_response=run.result.output,
                            is_expert_answer=validation_result.expert_answer is not None,
                            guardrailed=validation_result.should_guardrail,
                            escalated_to_sme=validation_result.escalated_to_sme,
                            scores=_format_eval_results(validation_result),
                        ),
                    ),
                )
                thread_to_messages[thread_id] = updated_message_history
            else:
                logger.warning("Unable to validate response with cleanlab. Missing `run.result`.")
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
        logger.exception("Error in airline chat streaming")
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


def _format_eval_results(
    validation_result: ProjectValidateResponse,
) -> dict[str, EvalResult]:
    eval_scores = {
        eval_key: EvalResult.model_validate(eval_result.model_dump())
        for eval_key, eval_result in validation_result.eval_scores.items()
    }
    deterministic_guardrails_results = (
        {
            guardrail_key: EvalResult(
                score=0.0 if guardrail_result.should_guardrail else None,
                triggered=guardrail_result.should_guardrail,
                triggered_guardrail=guardrail_result.should_guardrail,
            )
            for guardrail_key, guardrail_result in validation_result.deterministic_guardrails_results.items()
        }
        if validation_result.deterministic_guardrails_results is not None
        else {}
    )
    return {**eval_scores, **deterministic_guardrails_results}
