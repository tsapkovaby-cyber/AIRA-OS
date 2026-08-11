"""Stable-ID authorization; Telegram usernames are deliberately ignored."""

from enum import Enum


class Role(str, Enum):
    FOUNDER = "FOUNDER"
    UNKNOWN = "UNKNOWN"


class FounderAuthenticator:
    def __init__(self, founder_id: int | None):
        self._founder_id = founder_id

    def role_for(self, telegram_user_id: int) -> Role:
        if self._founder_id is not None and telegram_user_id == self._founder_id:
            return Role.FOUNDER
        return Role.UNKNOWN

    def setup_identity_message(self, telegram_user_id: int) -> str | None:
        """Expose the caller's numeric ID only while Founder ID is unconfigured."""
        if self._founder_id is not None:
            return None
        return f"Ваш Telegram ID для первоначальной настройки: {telegram_user_id}"

