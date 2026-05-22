from enum import Enum
from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime, timezone
import uuid


class MessageType(str, Enum):
    TASK_HANDOFF = "TASK_HANDOFF"
    CLARIFICATION_REQUEST = "CLARIFICATION_REQUEST"
    STATUS_UPDATE = "STATUS_UPDATE"
    COMPLETION_REPORT = "COMPLETION_REPORT"
    REJECTION = "REJECTION"
    ESCALATION = "ESCALATION"
    REVIEW_REQUEST = "REVIEW_REQUEST"
    REVIEW_DECISION = "REVIEW_DECISION"
    HUMAN_INTERVENTION = "HUMAN_INTERVENTION"


class ACPMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    thread_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    recipient_id: str
    message_type: MessageType
    body: str = Field(description="Natural language message body")
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    read: bool = False
