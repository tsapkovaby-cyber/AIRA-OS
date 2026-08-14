"""Architecture-first Memory Engine for AIRA.

This module provides an in-process reference implementation of the Memory API.
It is deliberately storage-provider neutral: JSON persistence demonstrates the
contracts while leaving vector search, database optimization, cloud sync, and AI
summarization out of scope for Sprint 003.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import (
    AuditEvent,
    MemoryImportance,
    MemoryRecord,
    MemoryStatus,
    MemoryType,
    MemoryVersion,
    Permission,
    Relationship,
    RelationshipType,
    SearchQuery,
    SecurityPolicy,
    new_id,
    utc_now,
    validate_non_empty,
    validate_percent,
)


class MemoryEngine:
    """Persistent, versioned, searchable, auditable memory architecture."""

    def __init__(self, storage_path: str | Path):
        self.storage_path = Path(storage_path)
        self.memories: dict[str, MemoryRecord] = {}
        self.relationships: dict[str, Relationship] = {}
        self.audit_log: list[AuditEvent] = []
        self.initialize()

    def initialize(self) -> None:
        """Create storage if needed and load the memory graph."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._persist()
            return
        data = json.loads(self.storage_path.read_text(encoding="utf-8") or "{}")
        self.memories = {item["id"]: MemoryRecord.from_dict(item) for item in data.get("memories", [])}
        self.relationships = {item["id"]: Relationship.from_dict(item) for item in data.get("relationships", [])}
        self.audit_log = [AuditEvent.from_dict(item) for item in data.get("audit_log", [])]

    def create_memory(
        self,
        *,
        memory_type: MemoryType,
        title: str,
        body: str,
        owner: str,
        source: str = "manual",
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        rating: int = 50,
        confidence: int = 50,
        tags: tuple[str, ...] = (),
        data: dict[str, Any] | None = None,
        agent_id: str | None = None,
        project_id: str | None = None,
        actor: str | None = None,
        security: SecurityPolicy | None = None,
    ) -> MemoryRecord:
        validate_non_empty(title, "title")
        validate_non_empty(owner, "owner")
        validate_percent(rating, "rating")
        validate_percent(confidence, "confidence")
        now = utc_now()
        policy = security or SecurityPolicy(owner=owner)
        version = MemoryVersion(
            version=1,
            title=title.strip(),
            body=body.strip(),
            data=data or {},
            source=source,
            rating=rating,
            confidence=confidence,
            tags=tuple(sorted(set(tags))),
            created_at=now,
            changed_by=actor or owner,
            change_reason="initial memory creation",
        )
        record = MemoryRecord(
            id=new_id("mem"),
            type=memory_type,
            importance=importance,
            status=MemoryStatus.ACTIVE,
            security=policy,
            current_version=1,
            versions=[version],
            created_at=now,
            updated_at=now,
            agent_id=agent_id,
            project_id=project_id,
        )
        self.memories[record.id] = record
        self._audit("create_memory", actor or owner, record.id, {"type": memory_type.value})
        self._persist()
        return record

    def update_memory(self, memory_id: str, *, actor: str, change_reason: str, **changes: Any) -> MemoryRecord:
        record = self._require_memory(memory_id)
        self._require_permission(record, actor, Permission.WRITE)
        current = record.current
        rating = int(changes.get("rating", current.rating))
        confidence = int(changes.get("confidence", current.confidence))
        validate_percent(rating, "rating")
        validate_percent(confidence, "confidence")
        version = MemoryVersion(
            version=record.current_version + 1,
            title=changes.get("title", current.title),
            body=changes.get("body", current.body),
            data=changes.get("data", current.data),
            source=changes.get("source", current.source),
            rating=rating,
            confidence=confidence,
            tags=tuple(sorted(set(changes.get("tags", current.tags)))),
            created_at=utc_now(),
            changed_by=actor,
            change_reason=change_reason,
        )
        record.versions.append(version)
        record.current_version = version.version
        record.updated_at = version.created_at
        self._audit("update_memory", actor, memory_id, {"version": version.version, "reason": change_reason})
        self._persist()
        return record

    def archive_memory(self, memory_id: str, *, actor: str, status: MemoryStatus = MemoryStatus.ARCHIVED) -> None:
        record = self._require_memory(memory_id)
        self._require_permission(record, actor, Permission.WRITE)
        if status == MemoryStatus.DELETED:
            raise ValueError("Use delete_memory for founder-authorized deletion")
        record.status = status
        record.updated_at = utc_now()
        self._audit("archive_memory", actor, memory_id, {"status": status.value})
        self._persist()

    def delete_memory(self, memory_id: str, *, actor: str, founder: str) -> None:
        if actor != founder:
            raise PermissionError("Only the Founder can delete memory")
        record = self._require_memory(memory_id)
        record.status = MemoryStatus.DELETED
        record.updated_at = utc_now()
        self._audit("delete_memory", actor, memory_id, {"policy": "founder_only_soft_delete"})
        self._persist()

    def restore_memory(self, memory_id: str, *, actor: str) -> None:
        record = self._require_memory(memory_id)
        self._require_permission(record, actor, Permission.ADMIN)
        record.status = MemoryStatus.ACTIVE
        record.updated_at = utc_now()
        self._audit("restore_memory", actor, memory_id, {})
        self._persist()

    def merge_memory(self, source_id: str, target_id: str, *, actor: str, reason: str) -> Relationship:
        source = self._require_memory(source_id)
        target = self._require_memory(target_id)
        self._require_permission(source, actor, Permission.WRITE)
        self._require_permission(target, actor, Permission.WRITE)
        source.status = MemoryStatus.MERGED
        return self.create_relationship(source_id, target_id, RelationshipType.MERGED_INTO, actor=actor, reason=reason)

    def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        *,
        actor: str,
        reason: str,
        confidence: int = 80,
    ) -> Relationship:
        self._require_memory(source_id)
        self._require_memory(target_id)
        validate_percent(confidence, "confidence")
        relationship = Relationship(new_id("rel"), source_id, target_id, relationship_type, reason, confidence, utc_now(), actor)
        self.relationships[relationship.id] = relationship
        self._audit("create_relationship", actor, source_id, {"target_id": target_id, "type": relationship_type.value})
        self._persist()
        return relationship

    def search_memory(self, query: SearchQuery, *, actor: str) -> list[MemoryRecord]:
        results = []
        related_ids = self._related_ids(query.relationship_to) if query.relationship_to else None
        for record in self.memories.values():
            if not record.security.can(actor, Permission.READ):
                continue
            current = record.current
            haystack = f"{current.title} {current.body} {' '.join(current.tags)}".lower()
            if query.text and query.text.lower() not in haystack:
                continue
            if query.tags and not set(query.tags).issubset(set(current.tags)):
                continue
            if query.memory_type and record.type != query.memory_type:
                continue
            if query.importance and record.importance != query.importance:
                continue
            if query.status and record.status != query.status:
                continue
            if query.agent_id and record.agent_id != query.agent_id:
                continue
            if related_ids is not None and record.id not in related_ids:
                continue
            if query.date_from and record.updated_at < query.date_from:
                continue
            if query.date_to and record.updated_at > query.date_to:
                continue
            results.append(record)
        return sorted(results, key=lambda item: (item.importance.value, item.updated_at), reverse=True)

    def summarize_memory(self, memory_id: str, *, actor: str) -> dict[str, Any]:
        record = self._require_memory(memory_id)
        self._require_permission(record, actor, Permission.READ)
        return {
            "id": record.id,
            "type": record.type.value,
            "status": record.status.value,
            "title": record.current.title,
            "summary": record.current.body[:240],
            "version": record.current_version,
            "confidence": record.current.confidence,
            "importance": record.importance.value,
            "tags": list(record.current.tags),
            "relationships": [r.to_dict() for r in self.relationships.values() if memory_id in (r.source_id, r.target_id)],
        }

    def _related_ids(self, memory_id: str) -> set[str]:
        ids = set()
        for relationship in self.relationships.values():
            if relationship.source_id == memory_id:
                ids.add(relationship.target_id)
            if relationship.target_id == memory_id:
                ids.add(relationship.source_id)
        return ids

    def _require_memory(self, memory_id: str) -> MemoryRecord:
        try:
            return self.memories[memory_id]
        except KeyError as exc:
            raise KeyError(f"Unknown memory: {memory_id}") from exc

    @staticmethod
    def _require_permission(record: MemoryRecord, actor: str, permission: Permission) -> None:
        if not record.security.can(actor, permission):
            raise PermissionError(f"{actor} lacks {permission.value} permission for {record.id}")

    def _audit(self, action: str, actor: str, memory_id: str | None, details: dict[str, Any]) -> None:
        self.audit_log.append(AuditEvent(new_id("audit"), action, actor, memory_id, details))

    def _persist(self) -> None:
        data = {
            "schema_version": "1.0",
            "memories": [memory.to_dict() for memory in self.memories.values()],
            "relationships": [relationship.to_dict() for relationship in self.relationships.values()],
            "audit_log": [event.to_dict() for event in self.audit_log],
        }
        self.storage_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
