"""Transport-neutral Telegram gateway models."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class Intent(StrEnum):
    CHAT = "CHAT"
    STATUS_QUERY = "STATUS_QUERY"
    RESEARCH_REQUEST = "RESEARCH_REQUEST"
    CONTENT_REQUEST = "CONTENT_REQUEST"
    APPROVAL_ACTION = "APPROVAL_ACTION"
    AGENT_CONTROL = "AGENT_CONTROL"
    WORKFLOW_CONTROL = "WORKFLOW_CONTROL"
    PUBLISHING_CONTROL = "PUBLISHING_CONTROL"
    KNOWLEDGE_QUERY = "KNOWLEDGE_QUERY"
    MEMORY_QUERY = "MEMORY_QUERY"
    SYSTEM_CONTROL = "SYSTEM_CONTROL"
    UNKNOWN = "UNKNOWN"


class Direction(StrEnum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


@dataclass(frozen=True, slots=True)
class FounderIdentity:
    telegram_user_id: int
    founder_user_id: str
    role: str
    permissions: frozenset[str]
    status: str = "ACTIVE"
    last_verified: datetime | None = None


@dataclass(frozen=True, slots=True)
class FounderMessage:
    message_id: str
    telegram_message_id: int
    telegram_update_id: int
    founder_user_id: str
    conversation_id: str
    direction: Direction
    text: str
    intent: Intent = Intent.UNKNOWN
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    workflow_reference: str | None = None
    memory_policy: str = "FOUNDER_PRIVATE"


@dataclass(frozen=True, slots=True)
class Button:
    label: str
    callback_data: str | None = None
    url: str | None = None


@dataclass(frozen=True, slots=True)
class GatewayResponse:
    text: str
    buttons: tuple[tuple[Button, ...], ...] = ()
    parse_mode: str | None = "MarkdownV2"


@dataclass(frozen=True, slots=True)
class CallbackAction:
    action: str
    object_type: str
    object_id: str
    version: int | None = None
    sensitive: bool = False


@dataclass(frozen=True, slots=True)
class TelegramUpdate:
    update_id: int
    user_id: int
    chat_id: int
    message_id: int
    text: str = ""
    callback_query_id: str | None = None
    callback_data: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)
