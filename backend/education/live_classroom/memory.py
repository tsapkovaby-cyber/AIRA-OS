"""Student-isolated summary memory; raw audio is deliberately excluded."""

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Protocol


class LearningMemory(Protocol):
    def save(self, student_id: str, session_id: str, summary: dict) -> None: ...
    def recent(self, student_id: str) -> list[dict]: ...


@dataclass
class InMemoryLearningMemory:
    _student_records: dict[str, dict[str, dict]] = field(default_factory=dict)

    def save(self, student_id: str, session_id: str, summary: dict) -> None:
        self._student_records.setdefault(student_id, {})[session_id] = deepcopy(summary)

    def recent(self, student_id: str) -> list[dict]:
        return [deepcopy(item) for item in self._student_records.get(student_id, {}).values()]
