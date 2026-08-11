from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class ResolvedPrompt:
    prompt_id: str
    version: str
    content: str
    prompt_hash: str


class PromptRegistry:
    def __init__(self):
        self._prompts = {}

    def register(self, prompt_id: str, version: str, content: str, *, agent="*", task="*", language="*"):
        self._prompts[(prompt_id, version, agent, task, language)] = content

    def resolve(self, prompt_id: str, version: str, *, agent="*", task="*", language="*") -> ResolvedPrompt:
        key = (prompt_id, version, agent, task, language)
        content = self._prompts[key]
        digest = hashlib.sha256(content.encode()).hexdigest()
        return ResolvedPrompt(prompt_id, version, content, digest)

