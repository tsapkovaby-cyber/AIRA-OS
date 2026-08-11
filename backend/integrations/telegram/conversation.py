"""Lightweight, replaceable recent-conversation storage and service."""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Sequence
from typing import Protocol

from .intelligence import AIRAIntelligenceProvider

ConversationKey = tuple[int, int]


class ConversationStore(Protocol):
    def get(self, key: ConversationKey) -> Sequence[dict[str, str]]: ...
    def append(self, key: ConversationKey, role: str, content: str) -> None: ...
    def delete_user(self, user_id: int) -> int: ...


class InMemoryConversationStore:
    """Process-local MVP store. Each (user, chat) pair has an independent window."""

    def __init__(self, max_messages: int = 20):
        self._items: dict[ConversationKey, deque[dict[str, str]]] = defaultdict(
            lambda: deque(maxlen=max_messages)
        )

    def get(self, key: ConversationKey) -> list[dict[str, str]]:
        return list(self._items.get(key, ()))

    def append(self, key: ConversationKey, role: str, content: str) -> None:
        self._items[key].append({"role": role, "content": content})

    def delete_user(self, user_id: int) -> int:
        keys = [key for key in self._items if key[0] == user_id]
        for key in keys:
            del self._items[key]
        return len(keys)


class AIRAConversationService:
    def __init__(self, provider: AIRAIntelligenceProvider, store: ConversationStore):
        self.provider = provider
        self.store = store

    async def respond(self, user_id: int, chat_id: int, message: str) -> str:
        key = (user_id, chat_id)
        prior = list(self.store.get(key))
        current = {"role": "user", "content": message}
        answer = await self.provider.generate_response([*prior, current])
        self.store.append(key, "user", message)
        self.store.append(key, "assistant", answer)
        return answer

    def delete_user_data(self, user_id: int) -> int:
        return self.store.delete_user(user_id)
