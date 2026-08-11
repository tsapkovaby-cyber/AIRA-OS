# AIRA-OS

AIRA-OS is the architecture workspace for AIRA.

## Sprint 003: Memory Engine

This repository now includes an architecture-first Memory Engine reference implementation in `aira_memory/` with tests and documentation.

### What is implemented

- Persistent JSON-backed memory store.
- Structured memory records for identity, knowledge, experience, conversation, project, research, content, decision, task, user, agent, system, and reference memory.
- Append-only memory versioning.
- Relationship graph mapping between memory records.
- Keyword, tag, type, relationship, date, importance, status, and agent search filters.
- Security policy with owner, visibility, permissions, and encryption metadata.
- Audit log for memory lifecycle events.

### What is intentionally out of scope

- LLM memory optimization.
- Vector implementation.
- Database optimization.
- Cloud synchronization.
- AI summarization.
- Provider, Telegram, or application integrations.

### Run tests

```bash
python -m pytest
```

### Minimal example

```python
from aira_memory import MemoryEngine
from aira_memory.models import MemoryType, RelationshipType, SearchQuery

engine = MemoryEngine(".aira/memory.json")
chatgpt = engine.create_memory(
    memory_type=MemoryType.KNOWLEDGE,
    title="ChatGPT",
    body="AI model knowledge object",
    owner="founder",
    confidence=95,
    tags=("ai", "models"),
)
models = engine.create_memory(
    memory_type=MemoryType.KNOWLEDGE,
    title="AI Models",
    body="Knowledge category",
    owner="founder",
)
engine.create_relationship(chatgpt.id, models.id, RelationshipType.BELONGS_TO, actor="founder", reason="taxonomy")
results = engine.search_memory(SearchQuery(text="ChatGPT"), actor="founder")
```

See `docs/memory-engine-architecture.md` for the architecture report.
