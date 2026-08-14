from __future__ import annotations

from dataclasses import dataclass

from .domain import Sensitivity


@dataclass(frozen=True)
class ContextItem:
    content: str
    sensitivity: Sensitivity
    priority: int = 5
    reference: str = ""
    is_instruction: bool = False


class ContextBuilder:
    """Builds least-context prompts while preserving instruction/data separation."""

    def build(self, instructions: list[ContextItem], data: list[ContextItem], *, budget: int,
              maximum_sensitivity: Sensitivity, permitted_private: bool = False) -> tuple[list[dict[str, str]], tuple[str, ...]]:
        if maximum_sensitivity == Sensitivity.SYSTEM_SECRET:
            raise ValueError("SYSTEM_SECRET must never enter model prompts")
        rank = list(Sensitivity).index
        allowed, remaining, refs = [], budget, []
        for item in sorted(instructions + data, key=lambda x: x.priority):
            if item.sensitivity == Sensitivity.SYSTEM_SECRET:
                continue
            if item.sensitivity == Sensitivity.FOUNDER_PRIVATE and not permitted_private:
                continue
            if rank(item.sensitivity) > rank(maximum_sensitivity):
                continue
            size = max(1, len(item.content.split()))
            if size > remaining:
                continue
            remaining -= size
            # Untrusted data is always a user message, never promoted to system policy.
            allowed.append({"role": "system" if item.is_instruction else "user", "content": item.content})
            if item.reference:
                refs.append(item.reference)
        return allowed, tuple(refs)

