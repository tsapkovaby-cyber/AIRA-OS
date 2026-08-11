# Sprint 003 Memory Engine Architecture Report

## Scope

Sprint 003 implements the architecture of AIRA's Memory Engine only. It does not add LLM memory optimization, vector infrastructure, database optimization, cloud synchronization, AI summarization, provider integrations, Telegram integrations, or application integrations.

## Design Principles

The engine treats memory as accumulated experience rather than transcript storage. Each memory is persistent, structured, versioned, searchable, explainable, auditable, secure, and expandable.

## Memory Pipeline

1. **Input** enters through the Memory API.
2. **Classification** is represented by `MemoryType`.
3. **Importance evaluation** is represented by `MemoryImportance`.
4. **Duplicate detection** is reserved for future policy layers.
5. **Version comparison** is implemented by append-only `MemoryVersion` history.
6. **Knowledge extraction** is represented by typed `data`, tags, source, rating, confidence, and body fields.
7. **Storage** is demonstrated with a JSON persistence adapter.
8. **Vector index** is intentionally out of scope.
9. **Relationship mapping** is implemented with typed graph edges.
10. **Ready** memories are available through keyword, tag, relationship, date, importance, type, status, and agent filters.

## Object Model

- `MemoryRecord`: identity, type, importance, status, security, versions, timestamps, optional agent/project ownership.
- `MemoryVersion`: append-only title, body, structured data, source, rating, confidence, tags, author, and change reason.
- `Relationship`: graph edge between two memories with typed relationship, reason, confidence, actor, and timestamp.
- `SecurityPolicy`: owner, visibility, actor permissions, and encryption flag.
- `AuditEvent`: append-only event log for create, update, archive, merge, delete, restore, and relationship operations.

## Memory Types

The architecture supports identity, knowledge, experience, conversation, project, research, content, decision, task, user, agent, system, and reference memories.

## Versioning and Forgetting

Memory is never overwritten. Updates append a new `MemoryVersion` and keep all previous versions. Deletion is a founder-only soft delete that sets status to `deleted`; records remain auditable. Other lifecycle states include archived, deprecated, merged, inactive, and historical.

## Search

The reference search implementation supports keyword, tag, memory type, importance, status, agent, relationship, and date filters. Semantic/vector search is intentionally deferred.

## Security

Every memory has an owner and security policy. Owners can read/write/administer their records by default. Additional actors can be granted read, write, or admin permissions. Unauthorized search results are hidden, and unauthorized mutation raises `PermissionError`.

## API Surface

The implemented API includes:

- `create_memory`
- `update_memory`
- `archive_memory`
- `search_memory`
- `summarize_memory`
- `merge_memory`
- `delete_memory`
- `restore_memory`
- `create_relationship`

## Migration Guide

The JSON store uses `schema_version: 1.0`. Future migrations should read the schema version, transform records into the latest dataclass fields, append a migration audit event, and persist the upgraded store without deleting historical versions.

## Schema Reference

### MemoryRecord

| Field | Purpose |
| --- | --- |
| `id` | Stable memory identifier. |
| `type` | Memory classification. |
| `importance` | Critical, high, medium, low, or temporary. |
| `status` | Active, archived, deprecated, merged, inactive, historical, or deleted. |
| `security` | Owner, visibility, permissions, and encryption metadata. |
| `current_version` | Pointer to the latest version number. |
| `versions` | Append-only history of `MemoryVersion` objects. |
| `agent_id` | Optional independent agent memory owner. |
| `project_id` | Optional project memory scope. |

### MemoryVersion

| Field | Purpose |
| --- | --- |
| `version` | Monotonic version number. |
| `title` / `body` | Human-readable knowledge or experience. |
| `data` | Structured facts, decisions, observations, or metadata. |
| `source` | Origin of the memory. |
| `rating` | Quality rating from 0 to 100. |
| `confidence` | Confidence score from 0 to 100. |
| `tags` | Search and classification tags. |
| `changed_by` / `change_reason` | Explainability for each update. |

### Relationship

Relationships connect two memories into a graph using types such as `belongs_to`, `connected_with`, `used_in`, `mentioned_in`, `recommended_by`, `derived_from`, `supersedes`, `supports`, `contradicts`, and `merged_into`.

## Interface Reference

The public Python interface is exported from `aira_memory`:

```python
from aira_memory import MemoryEngine
```

`MemoryEngine` exposes the Sprint 003 Memory API: create, update, archive, search, summarize, merge, delete, restore, and relationship creation. All mutating operations write an audit event and persist the JSON store.

## Test Coverage

Unit tests cover initialization, memory creation and validation, append-only versioning, search filters, relationship graph traversal, permission enforcement, archive lifecycle, and founder-only delete policy.
