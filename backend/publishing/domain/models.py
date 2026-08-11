"""Publishing domain values. This module has no platform dependencies."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PublicationStatus(StrEnum):
    DRAFT = "DRAFT"
    NOT_APPROVED = "NOT_APPROVED"
    APPROVED = "APPROVED"
    QUEUED = "QUEUED"
    SCHEDULED = "SCHEDULED"
    PREPARING = "PREPARING"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    PARTIALLY_PUBLISHED = "PARTIALLY_PUBLISHED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    CANCELLED = "CANCELLED"
    ARCHIVED = "ARCHIVED"


class ApprovalStatus(StrEnum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PENDING = "PENDING"


class ContentStatus(StrEnum):
    READY_TO_PUBLISH = "READY_TO_PUBLISH"
    DRAFT = "DRAFT"


class FailureCategory(StrEnum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    RATE_LIMIT = "RATE_LIMIT"
    NETWORK_ERROR = "NETWORK_ERROR"
    PLATFORM_ERROR = "PLATFORM_ERROR"
    MEDIA_ERROR = "MEDIA_ERROR"
    PERMISSION_ERROR = "PERMISSION_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


RECOVERABLE_FAILURES = {FailureCategory.RATE_LIMIT, FailureCategory.NETWORK_ERROR, FailureCategory.PLATFORM_ERROR}


@dataclass(frozen=True)
class Approval:
    approval_id: str
    status: ApprovalStatus
    content_id: str
    content_version: int


@dataclass(frozen=True)
class MediaAsset:
    asset_id: str
    content_id: str
    version: int
    checksum: str
    format: str
    approved: bool


@dataclass(frozen=True)
class ContentSnapshot:
    content_id: str
    version: int
    status: ContentStatus
    checksum: str
    media_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class Account:
    account_id: str
    platform: str
    display_name: str
    external_account_id: str
    credential_reference: str
    permissions: frozenset[str]
    enabled: bool = True


@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    publication_id: str
    timestamp: datetime
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PublicationReceipt:
    publication_id: str
    platform: str
    external_id: str
    published_at: datetime
    content_version: int
    account_id: str
    checksum: str
    response_metadata: dict[str, Any] = field(default_factory=dict)
    public_url: str | None = None


@dataclass
class Publication:
    publication_id: str
    content_id: str
    content_version: int
    workflow_id: str
    platform: str
    account_id: str
    publication_type: str
    guardian_approval_id: str
    founder_approval_id: str
    idempotency_key: str
    platform_adapter: str
    requested_at: datetime
    timezone: str = "UTC"
    local_display_time: str | None = None
    scheduled_at_utc: datetime | None = None
    status: PublicationStatus = PublicationStatus.DRAFT
    published_at: datetime | None = None
    external_publication_id: str | None = None
    retry_count: int = 0
    error_state: FailureCategory | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    audit_history: list[AuditEvent] = field(default_factory=list)


@dataclass(frozen=True)
class AdapterResult:
    external_id: str
    checksum: str
    metadata: dict[str, Any] = field(default_factory=dict)
    public_url: str | None = None


class PublishingError(Exception):
    category = FailureCategory.UNKNOWN_ERROR


class ValidationError(PublishingError):
    category = FailureCategory.VALIDATION_ERROR


class AdapterError(PublishingError):
    def __init__(self, message: str, category: FailureCategory):
        super().__init__(message)
        self.category = category


class UnsupportedOperation(PublishingError):
    pass
