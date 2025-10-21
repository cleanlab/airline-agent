import uuid
from enum import StrEnum

from pydantic import BaseModel

from airline_agent.backend.schemas.message import AgentMessage
from airline_agent.backend.schemas.run import Run


class RunEventObject(StrEnum):
    THREAD_RUN_IN_PROGRESS = "thread.run.in_progress"
    THREAD_MESSAGE = "thread.message"
    THREAD_RUN_COMPLETED = "thread.run.completed"
    THREAD_RUN_FAILED = "thread.run.failed"


class RunEventBase(BaseModel):
    id: uuid.UUID
    object: RunEventObject
    data: AgentMessage | Run

    def to_sse(self) -> str:
        """Render the event to a string for SSE."""
        return f"event: {self.object}\ndata: {self.model_dump_json(exclude_none=True)}\n\n"


class RunEventThreadRunInProgress(RunEventBase):
    object: RunEventObject = RunEventObject.THREAD_RUN_IN_PROGRESS
    data: Run


class RunEventThreadMessage(RunEventBase):
    object: RunEventObject = RunEventObject.THREAD_MESSAGE
    data: AgentMessage


class RunEventThreadRunCompleted(RunEventBase):
    object: RunEventObject = RunEventObject.THREAD_RUN_COMPLETED
    data: Run


class RunEventThreadRunFailed(RunEventBase):
    object: RunEventObject = RunEventObject.THREAD_RUN_FAILED
    data: Run


RunEvent = RunEventThreadRunInProgress | RunEventThreadMessage | RunEventThreadRunCompleted | RunEventThreadRunFailed
