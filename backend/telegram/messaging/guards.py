"""In-process transport guards; production stores can implement the same API."""

import time
from collections import defaultdict, deque


class DuplicateUpdate(Exception):
    pass


class RateLimitExceeded(Exception):
    pass


class IdempotencyStore:
    def __init__(self) -> None:
        self._seen: set[str] = set()

    def claim(self, key: str) -> None:
        if key in self._seen:
            raise DuplicateUpdate(key)
        self._seen.add(key)


class SlidingWindowRateLimiter:
    def __init__(self, *, requests: int = 30, window_seconds: int = 60) -> None:
        self._requests = requests
        self._window = window_seconds
        self._events: dict[int, deque[float]] = defaultdict(deque)

    def check(self, user_id: int, *, now: float | None = None) -> None:
        current = time.monotonic() if now is None else now
        events = self._events[user_id]
        while events and events[0] <= current - self._window:
            events.popleft()
        if len(events) >= self._requests:
            raise RateLimitExceeded("rate limit exceeded")
        events.append(current)
