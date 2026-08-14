"""Flow-preserving correction selection."""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True)
class Correction:
    original: str
    corrected: str
    explanation: str
    category: str
    meaning_breaking: bool = False
    repeated: bool = False
    lesson_target: bool = False
    high_frequency: bool = False
    pronunciation: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def priority(self) -> int:
        if self.meaning_breaking:
            return 1
        if self.repeated:
            return 2
        if self.lesson_target:
            return 3
        if self.high_frequency:
            return 4
        if self.pronunciation:
            return 5
        return 6


class CorrectionBuffer:
    def __init__(self, release_every_turns: int = 3, maximum_release: int = 1):
        self._items: list[Correction] = []
        self.release_every_turns = release_every_turns
        self.maximum_release = maximum_release

    def add(self, correction: Correction) -> None:
        self._items.append(correction)

    def select(self, turn_number: int, force: bool = False) -> list[Correction]:
        immediate = [item for item in self._items if item.meaning_breaking]
        if not force and not immediate and turn_number % self.release_every_turns:
            return []
        selected = sorted(self._items, key=lambda item: (item.priority, item.created_at))[
            : self.maximum_release
        ]
        for item in selected:
            self._items.remove(item)
        return selected

    def __len__(self) -> int:
        return len(self._items)
