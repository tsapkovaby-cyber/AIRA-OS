from collections import deque


class InMemoryPublishingQueue:
    """Deterministic reference queue. Production implementations provide durable locks."""
    def __init__(self):
        self._items, self._cancelled, self.paused = deque(), set(), False

    def enqueue(self, publication_id: str, scheduled_at=None) -> None:
        if publication_id not in self._items:
            self._items.append(publication_id)

    def next(self) -> str | None:
        if self.paused:
            return None
        while self._items:
            item = self._items.popleft()
            if item not in self._cancelled:
                return item
        return None

    def cancel(self, publication_id: str) -> None:
        self._cancelled.add(publication_id)

    def pause(self) -> None: self.paused = True
    def resume(self) -> None: self.paused = False
    def inspect(self) -> tuple[str, ...]: return tuple(self._items)

