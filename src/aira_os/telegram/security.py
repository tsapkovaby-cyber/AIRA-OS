from __future__ import annotations

import hmac
import logging
import re
import time
from collections import defaultdict, deque


class RedactingFilter(logging.Filter):
    def __init__(self, secrets: list[str]):
        super().__init__()
        self.secrets = [secret for secret in secrets if secret]

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        for secret in self.secrets:
            message = message.replace(secret, "[REDACTED]")
        message = re.sub(r"bot\d+:[A-Za-z0-9_-]+", "bot[REDACTED]", message)
        record.msg, record.args = message, ()
        return True


class Security:
    def __init__(self, founder_id: int, webhook_secret: str, private_mode: bool = True):
        self.founder_id, self.webhook_secret, self.private_mode = founder_id, webhook_secret, private_mode
        self.hits: dict[int, deque[float]] = defaultdict(deque)

    def verify_webhook(self, supplied: str) -> bool:
        return hmac.compare_digest(supplied or "", self.webhook_secret)

    def is_founder(self, user_id: int) -> bool:
        return user_id == self.founder_id

    def authorize(self, user_id: int) -> bool:
        return self.is_founder(user_id) or not self.private_mode

    def rate_limit(self, user_id: int) -> bool:
        window, maximum = 60.0, (120 if self.is_founder(user_id) else 20)
        queue = self.hits[user_id]; cutoff = time.monotonic() - window
        while queue and queue[0] < cutoff: queue.popleft()
        if len(queue) >= maximum: return False
        queue.append(time.monotonic()); return True
