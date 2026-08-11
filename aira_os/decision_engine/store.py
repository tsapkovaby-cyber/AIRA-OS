"""In-memory decision repository for architecture validation.

Persistent storage integrations are intentionally out of scope for Sprint 006.
"""

from __future__ import annotations

from .models import Decision


class DecisionStore:
    """Simple repository preserving decisions and their history."""

    def __init__(self) -> None:
        self._decisions: dict[str, Decision] = {}

    def save(self, decision: Decision) -> Decision:
        self._decisions[decision.id] = decision
        return decision

    def load(self, decision_id: str) -> Decision:
        return self._decisions[decision_id]

    def search(self, query: str) -> list[Decision]:
        normalized = query.lower()
        return [
            decision
            for decision in self._decisions.values()
            if normalized in decision.goal.lower() or normalized in decision.reasoning.lower()
        ]

    def archive(self, decision_id: str) -> Decision:
        decision = self.load(decision_id)
        decision.record("archive", "system", "Decision archived for historical retention.")
        return decision
