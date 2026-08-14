"""In-memory Research API for Sprint 005 architecture validation.

This module intentionally avoids external integrations, web scraping, browser
automation, scheduled jobs, background workers, autonomous publishing, and AI
summarization.
"""

from __future__ import annotations

from dataclasses import asdict

from .models import KnowledgeCandidate, ResearchItem
from .services import ResearchPipeline, detect_duplicates, validate_discovery


class ResearchRepository:
    def __init__(self) -> None:
        self._items: dict[str, ResearchItem] = {}

    def create_item(self, item: ResearchItem) -> ResearchItem:
        validate_discovery(item)
        duplicates = detect_duplicates([*self._items.values(), item])
        self._items[item.item_id] = item
        item.history.append(f"created;duplicates_checked={len(duplicates)}")
        return item

    def update_item(self, item_id: str, **changes: object) -> ResearchItem:
        item = self._items[item_id]
        for field_name, value in changes.items():
            if not hasattr(item, field_name):
                raise AttributeError(field_name)
            setattr(item, field_name, value)
        validate_discovery(item)
        item.history.append("updated")
        return item

    def archive_item(self, item_id: str) -> ResearchItem:
        item = self._items[item_id]
        item.archived = True
        item.history.append("archived")
        return item

    def search(self, query: str) -> list[ResearchItem]:
        needle = query.casefold()
        return [
            item
            for item in self._items.values()
            if needle in item.title.casefold()
            or needle in item.summary.casefold()
            or any(needle in tag.casefold() for tag in item.tags)
        ]

    def export_item(self, item_id: str) -> dict[str, object]:
        return asdict(self._items[item_id])

    def import_item(self, item: ResearchItem) -> ResearchItem:
        return self.create_item(item)

    def validate(self, item_id: str) -> bool:
        validate_discovery(self._items[item_id])
        return True

    def summarize(self, item_id: str) -> str:
        item = self._items[item_id]
        return item.summary


class ResearchAPI:
    def __init__(self, repository: ResearchRepository | None = None, pipeline: ResearchPipeline | None = None) -> None:
        self.repository = repository or ResearchRepository()
        self.pipeline = pipeline or ResearchPipeline()

    def create_item(self, item: ResearchItem) -> ResearchItem:
        return self.repository.create_item(item)

    def update_item(self, item_id: str, **changes: object) -> ResearchItem:
        return self.repository.update_item(item_id, **changes)

    def archive_item(self, item_id: str) -> ResearchItem:
        return self.repository.archive_item(item_id)

    def search(self, query: str) -> list[ResearchItem]:
        return self.repository.search(query)

    def export_item(self, item_id: str) -> dict[str, object]:
        return self.repository.export_item(item_id)

    def import_item(self, item: ResearchItem) -> ResearchItem:
        return self.repository.import_item(item)

    def validate(self, item_id: str) -> bool:
        return self.repository.validate(item_id)

    def summarize(self, item_id: str) -> str:
        return self.repository.summarize(item_id)

    def forward_candidate(self, item_id: str) -> KnowledgeCandidate:
        return self.pipeline.process(self.repository._items[item_id])
