from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timezone
from enum import IntEnum


class NotificationLevel(IntEnum):
    INFO = 10
    ACTION_REQUIRED = 20
    WARNING = 30
    CRITICAL = 40


@dataclass
class NotificationPolicy:
    """Spam-safe policy seam for proactive Founder notifications."""
    minimum_level: NotificationLevel = NotificationLevel.INFO
    quiet_start: time | None = None
    quiet_end: time | None = None
    sent_keys: set[str] = field(default_factory=set)

    def allows(self, level: NotificationLevel, key: str, at: datetime | None = None) -> bool:
        if key in self.sent_keys or level < self.minimum_level:
            return False
        current = (at or datetime.now(timezone.utc)).timetz().replace(tzinfo=None)
        quiet = False
        if self.quiet_start is not None and self.quiet_end is not None:
            quiet = (self.quiet_start <= current < self.quiet_end if self.quiet_start < self.quiet_end
                     else current >= self.quiet_start or current < self.quiet_end)
        if quiet and level < NotificationLevel.CRITICAL:
            return False
        self.sent_keys.add(key)
        return True
