import uuid
from enum import StrEnum

from pydantic import BaseModel

from airline_agent.backend.schemas.message import AgentMessage


class RunStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Run(BaseModel):
    id: uuid.UUID
    status: RunStatus
    thread_id: str


class RunWithMessageHistory(Run):
    message_history: list[AgentMessage]
