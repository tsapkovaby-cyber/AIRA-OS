from pathlib import Path

import pytest

from aira_memory import MemoryEngine
from aira_memory.models import MemoryImportance, MemoryStatus, MemoryType, RelationshipType, SearchQuery


def engine(tmp_path: Path) -> MemoryEngine:
    return MemoryEngine(tmp_path / "memory.json")


def test_initialization_creates_store(tmp_path):
    memory = engine(tmp_path)
    assert memory.storage_path.exists()
    assert memory.memories == {}


def test_memory_creation_validates_objects(tmp_path):
    memory = engine(tmp_path)
    record = memory.create_memory(memory_type=MemoryType.IDENTITY, title="AIRA", body="Mission memory", owner="founder", confidence=98)
    assert record.current.title == "AIRA"
    assert record.current.confidence == 98
    with pytest.raises(ValueError):
        memory.create_memory(memory_type=MemoryType.KNOWLEDGE, title="", body="invalid", owner="founder")


def test_versioning_never_overwrites(tmp_path):
    memory = engine(tmp_path)
    record = memory.create_memory(memory_type=MemoryType.KNOWLEDGE, title="Prompting", body="v1", owner="founder")
    memory.update_memory(record.id, actor="founder", change_reason="verified source", body="v2", confidence=90)
    assert record.current_version == 2
    assert [version.body for version in record.versions] == ["v1", "v2"]


def test_keyword_tag_type_importance_and_agent_search(tmp_path):
    memory = engine(tmp_path)
    memory.create_memory(
        memory_type=MemoryType.EXPERIENCE,
        title="Midjourney test",
        body="Generated images and recommended usage",
        owner="founder",
        importance=MemoryImportance.HIGH,
        tags=("image", "ai"),
        agent_id="research-agent",
    )
    results = memory.search_memory(
        SearchQuery(text="recommended", tags=("ai",), memory_type=MemoryType.EXPERIENCE, importance=MemoryImportance.HIGH, agent_id="research-agent"),
        actor="founder",
    )
    assert len(results) == 1


def test_relationship_search_and_summary(tmp_path):
    memory = engine(tmp_path)
    model = memory.create_memory(memory_type=MemoryType.KNOWLEDGE, title="ChatGPT", body="AI model", owner="founder")
    category = memory.create_memory(memory_type=MemoryType.KNOWLEDGE, title="AI Models", body="Category", owner="founder")
    relationship = memory.create_relationship(model.id, category.id, RelationshipType.BELONGS_TO, actor="founder", reason="taxonomy")
    assert relationship.type == RelationshipType.BELONGS_TO
    assert memory.search_memory(SearchQuery(relationship_to=model.id), actor="founder")[0].id == category.id
    assert memory.summarize_memory(model.id, actor="founder")["relationships"][0]["target_id"] == category.id


def test_permissions_are_enforced(tmp_path):
    memory = engine(tmp_path)
    record = memory.create_memory(memory_type=MemoryType.USER, title="Preference", body="Approved preference", owner="founder")
    assert memory.search_memory(SearchQuery(text="Preference"), actor="stranger") == []
    with pytest.raises(PermissionError):
        memory.update_memory(record.id, actor="stranger", change_reason="not allowed", body="bad")


def test_founder_only_delete_and_archive(tmp_path):
    memory = engine(tmp_path)
    record = memory.create_memory(memory_type=MemoryType.DECISION, title="Architecture", body="JSON reference store", owner="founder")
    memory.archive_memory(record.id, actor="founder")
    assert record.status == MemoryStatus.ARCHIVED
    with pytest.raises(PermissionError):
        memory.delete_memory(record.id, actor="agent", founder="founder")
    memory.delete_memory(record.id, actor="founder", founder="founder")
    assert record.status == MemoryStatus.DELETED
