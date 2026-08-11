"""Replaceable conversation-memory boundary and process-local MVP implementation."""
from typing import Protocol


class ConversationMemory(Protocol):
    def history(self, user_id: int) -> list[dict[str, str]]: ...
    def append(self, user_id: int, role: str, content: str) -> None: ...
    def delete(self, user_id: int) -> None: ...


class ProcessLocalConversationMemory:
    """Memory that is deliberately lost when the service restarts."""

    def __init__(self, max_messages: int = 20) -> None:
        self._messages: dict[int, list[dict[str, str]]] = {}
        self._max_messages = max_messages

    def history(self, user_id: int) -> list[dict[str, str]]:
        return list(self._messages.get(user_id, []))

    def append(self, user_id: int, role: str, content: str) -> None:
        messages = self._messages.setdefault(user_id, [])
        messages.append({"role": role, "content": content})
        del messages[:-self._max_messages]

    def delete(self, user_id: int) -> None:
        self._messages.pop(user_id, None)
