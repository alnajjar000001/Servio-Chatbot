from pydantic import BaseModel, Field
from typing import Any, Optional
from enum import Enum


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str


class SessionContext(BaseModel):
    """Stateless session carrier — sent by the frontend on every request and returned updated."""
    customer_id: str = ""
    customer_name: str = ""
    primary_location_id: str = ""
    customer_phone: str = ""


class ChatRequest(BaseModel):
    message: str
    conversation_history: list[ChatMessage] = []
    session_context: SessionContext = Field(default_factory=SessionContext)


class ToolCallInfo(BaseModel):
    tool_name: str
    tool_input: dict[str, Any]
    tool_result: Any


class ChatResponse(BaseModel):
    response: str
    tool_calls: list[ToolCallInfo] = []
    customer_data: Optional[dict[str, Any]] = None
    session_context: SessionContext = Field(default_factory=SessionContext)
