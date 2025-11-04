from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, TypeAdapter


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class EvalLog(BaseModel):
    explanation: str | None = None


class EvalResult(BaseModel):
    score: float | None = None
    triggered: bool | None = None
    triggered_escalation: bool | None = None
    triggered_guardrail: bool | None = None
    log: EvalLog | None = None


ResponseScoreMetadata = dict[str, EvalResult]
ResponseScoreMetadataAdapter = TypeAdapter(ResponseScoreMetadata)


class MessageMetadata(BaseModel):
    original_llm_response: str | None = None
    is_expert_answer: bool | None = None
    guardrailed: bool | None = None
    escalated_to_sme: bool | None = None
    scores: ResponseScoreMetadata | None = None
    log_id: str | None = None


class ToolCall(BaseModel):
    tool_call_id: str
    tool_name: str
    arguments: str | None
    result: str | None = None
    error: str | None = None


class MessageBase(BaseModel):
    thread_id: str
    metadata: MessageMetadata = Field(default_factory=MessageMetadata)


class ToolCallMessage(MessageBase):
    role: Literal[MessageRole.TOOL] = MessageRole.TOOL
    content: ToolCall


class UserMessage(MessageBase):
    role: Literal[MessageRole.USER] = MessageRole.USER
    content: str


class AssistantMessage(MessageBase):
    role: Literal[MessageRole.ASSISTANT] = MessageRole.ASSISTANT
    content: str


AgentMessage = ToolCallMessage | UserMessage | AssistantMessage
