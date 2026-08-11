"""Structured models for AIRA's architecture-first Memory Engine.

The engine intentionally uses only Python's standard library. It defines the
persistence, versioning, validation, search, relationship, permission, and audit
contracts needed before adding vector stores, databases, or LLM integrations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    """Return an ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class MemoryType(str, Enum):
    IDENTITY = "identity"
    KNOWLEDGE = "knowledge"
    EXPERIENCE = "experience"
    CONVERSATION = "conversation"
    PROJECT = "project"
    RESEARCH = "research"
    CONTENT = "content"
    DECISION = "decision"
    TASK = "task"
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    REFERENCE = "reference"


class MemoryImportance(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    TEMPORARY = "temporary"


class MemoryStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"
    MERGED = "merged"
    INACTIVE = "inactive"
    HISTORICAL = "historical"
    DELETED = "deleted"


class Visibility(str, Enum):
    PRIVATE = "private"
    AGENT = "agent"
    PROJECT = "project"
    PUBLIC = "public"


class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class RelationshipType(str, Enum):
    BELONGS_TO = "belongs_to"
    CONNECTED_WITH = "connected_with"
    USED_IN = "used_in"
    MENTIONED_IN = "mentioned_in"
    RECOMMENDED_BY = "recommended_by"
    DERIVED_FROM = "derived_from"
    SUPERSEDES = "supersedes"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    MERGED_INTO = "merged_into"


@dataclass(frozen=True)
class SecurityPolicy:
    owner: str
    visibility: Visibility = Visibility.PRIVATE
    permissions: dict[str, set[Permission]] = field(default_factory=dict)
    encrypted: bool = False

    def can(self, actor: str, permission: Permission) -> bool:
        if actor == self.owner:
            return True
        actor_permissions = self.permissions.get(actor, set())
        return permission in actor_permissions or Permission.ADMIN in actor_permissions

    def to_dict(self) -> dict[str, Any]:
        return {
            "owner": self.owner,
            "visibility": self.visibility.value,
            "permissions": {k: sorted(p.value for p in v) for k, v in self.permissions.items()},
            "encrypted": self.encrypted,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SecurityPolicy":
        return cls(
            owner=data["owner"],
            visibility=Visibility(data.get("visibility", Visibility.PRIVATE.value)),
            permissions={k: {Permission(item) for item in v} for k, v in data.get("permissions", {}).items()},
            encrypted=bool(data.get("encrypted", False)),
        )


@dataclass(frozen=True)
class MemoryVersion:
    version: int
    title: str
    body: str
    data: dict[str, Any]
    source: str
    rating: int
    confidence: int
    tags: tuple[str, ...]
    created_at: str
    changed_by: str
    change_reason: str

    def to_dict(self) -> dict[str, Any]:
        result = self.__dict__.copy()
        result["tags"] = list(self.tags)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryVersion":
        return cls(**{**data, "tags": tuple(data.get("tags", []))})


@dataclass
class MemoryRecord:
    id: str
    type: MemoryType
    importance: MemoryImportance
    status: MemoryStatus
    security: SecurityPolicy
    current_version: int
    versions: list[MemoryVersion]
    created_at: str
    updated_at: str
    agent_id: str | None = None
    project_id: str | None = None

    @property
    def current(self) -> MemoryVersion:
        return self.versions[self.current_version - 1]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "importance": self.importance.value,
            "status": self.status.value,
            "security": self.security.to_dict(),
            "current_version": self.current_version,
            "versions": [v.to_dict() for v in self.versions],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "agent_id": self.agent_id,
            "project_id": self.project_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryRecord":
        return cls(
            id=data["id"],
            type=MemoryType(data["type"]),
            importance=MemoryImportance(data["importance"]),
            status=MemoryStatus(data["status"]),
            security=SecurityPolicy.from_dict(data["security"]),
            current_version=int(data["current_version"]),
            versions=[MemoryVersion.from_dict(v) for v in data["versions"]],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            agent_id=data.get("agent_id"),
            project_id=data.get("project_id"),
        )


@dataclass(frozen=True)
class Relationship:
    id: str
    source_id: str
    target_id: str
    type: RelationshipType
    reason: str
    confidence: int
    created_at: str
    created_by: str

    def to_dict(self) -> dict[str, Any]:
        return {**self.__dict__, "type": self.type.value}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Relationship":
        return cls(**{**data, "type": RelationshipType(data["type"])})


@dataclass(frozen=True)
class AuditEvent:
    id: str
    action: str
    actor: str
    memory_id: str | None
    details: dict[str, Any]
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AuditEvent":
        return cls(**data)


@dataclass(frozen=True)
class SearchQuery:
    text: str | None = None
    tags: tuple[str, ...] = ()
    memory_type: MemoryType | None = None
    importance: MemoryImportance | None = None
    status: MemoryStatus | None = None
    agent_id: str | None = None
    relationship_to: str | None = None
    date_from: str | None = None
    date_to: str | None = None


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def validate_percent(value: int, field_name: str) -> None:
    if not 0 <= value <= 100:
        raise ValueError(f"{field_name} must be between 0 and 100")


def validate_non_empty(value: str, field_name: str) -> None:
    if not value or not value.strip():
        raise ValueError(f"{field_name} is required")
