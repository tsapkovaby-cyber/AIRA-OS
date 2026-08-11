from collections import defaultdict

from ..domain.events import ContentEvent
from ..domain.models import Content
from ..domain.errors import ContentError


class InMemoryContentRepository:
    def __init__(self) -> None:
        self._items: dict[str, list[Content]] = defaultdict(list)

    def save_version(self, content: Content) -> None:
        content.validate()
        versions = self._items[content.content_id]
        if any(item.version == content.version for item in versions):
            raise ContentError("a stored version is immutable")
        if versions and content.version != versions[-1].version + 1:
            raise ContentError("versions must be sequential")
        versions.append(content)

    def get(self, content_id: str, version: int | None = None) -> Content:
        items = self._items[content_id]
        if not items:
            raise KeyError(content_id)
        return items[-1] if version is None else next(i for i in items if i.version == version)

    def history(self, content_id: str) -> tuple[Content, ...]:
        return tuple(self._items.get(content_id, ()))

    def find_related(self, topic: str) -> tuple[Content, ...]:
        needle = topic.casefold()
        return tuple(item for versions in self._items.values() for item in versions[-1:]
                     if needle in item.topic.casefold() or item.topic.casefold() in needle)


class RecordingEventPublisher:
    def __init__(self) -> None:
        self.events: list[ContentEvent] = []

    def publish(self, event: ContentEvent) -> None:
        self.events.append(event)
