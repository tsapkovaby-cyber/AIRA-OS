from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
import uuid


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MessageType(StrEnum):
    TEXT = "TEXT"
    VOICE = "VOICE"
    PHOTO = "PHOTO"
    VIDEO = "VIDEO"
    DOCUMENT = "DOCUMENT"
    AUDIO = "AUDIO"
    REPLY = "REPLY"
    BUTTON_CALLBACK = "BUTTON_CALLBACK"
    COMMAND = "COMMAND"


class ProcessingStatus(StrEnum):
    RECEIVED = "RECEIVED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    WAITING_TOOL = "WAITING_TOOL"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ConversationMode(StrEnum):
    NORMAL = "NORMAL"
    FOUNDER = "FOUNDER"
    RESEARCH = "RESEARCH"
    CONTENT = "CONTENT"
    EXPERIMENT = "EXPERIMENT"
    REVIEW = "REVIEW"
    DEBUG = "DEBUG"


@dataclass
class TelegramMessage:
    message_id: int
    chat_id: int
    user_id: int
    type: MessageType
    text: str = ""
    media_references: list[dict[str, Any]] = field(default_factory=list)
    reply_context: dict[str, Any] | None = None
    timestamp: int = 0
    telegram_update_id: int = 0
    processing_status: ProcessingStatus = ProcessingStatus.RECEIVED
    callback_data: str = ""


@dataclass
class ConversationSession:
    telegram_chat_id: int
    telegram_user_id: int
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    platform: str = "telegram"
    aira_identity_version: str = "canonical"
    conversation_mode: ConversationMode = ConversationMode.FOUNDER
    memory_context: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=now)
    last_active: str = field(default_factory=now)
    status: str = "ACTIVE"


@dataclass
class ActionProposal:
    action: str
    reason: str
    requested_by: int
    proposal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    risk: str = "LOW"
    cost: float = 0.0
    preview: str = ""
    created_at: str = field(default_factory=now)
    approval_status: str = "PENDING"
    expires_at: str | None = None
