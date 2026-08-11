from dataclasses import dataclass, field
from datetime import datetime
from typing import Mapping

from .models import utcnow


@dataclass(frozen=True)
class ContentEvent:
    name: str
    content_id: str
    workflow_id: str | None = None
    payload: Mapping[str, str] = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=utcnow)


EVENT_NAMES = frozenset({
    "ContentRequested", "ContentBriefCreated", "DraftCreated", "DraftUpdated",
    "ContentSentToGuardian", "RevisionRequested", "ContentApprovedByGuardian",
    "ContentApprovedByFounder", "ContentRejected", "ContentReadyForPublishing",
})
