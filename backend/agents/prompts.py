"""Versioned prompt registry; prompt content is referenced, not scattered in code."""

from dataclasses import dataclass, field
from datetime import datetime

from .domain import AgentType, utcnow


@dataclass(frozen=True)
class PromptDefinition:
    prompt_id: str
    agent_type: AgentType
    version: str
    content_reference: str
    status: str = "APPROVED"
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
    approved_by: str | None = None


class PromptRegistry:
    def __init__(self) -> None:
        self._prompts: dict[tuple[str, str], PromptDefinition] = {}

    def register(self, prompt: PromptDefinition) -> None:
        key = (prompt.prompt_id, prompt.version)
        if key in self._prompts:
            raise ValueError("duplicate prompt version")
        self._prompts[key] = prompt

    def resolve(self, prompt_id: str, version: str | None = None) -> PromptDefinition:
        matches = [p for (pid, _), p in self._prompts.items() if pid == prompt_id and p.status == "APPROVED"]
        if version is not None:
            matches = [p for p in matches if p.version == version]
        if not matches:
            raise KeyError(f"approved prompt not found: {prompt_id}")
        return max(matches, key=lambda p: tuple(int(n) for n in p.version.split(".")))

    def contains(self, prompt_id: str) -> bool:
        try:
            self.resolve(prompt_id)
            return True
        except KeyError:
            return False
