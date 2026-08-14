"""Identity authentication based only on immutable Telegram user IDs."""

from datetime import datetime, timezone

from ..schemas.models import FounderIdentity


class AuthenticationError(Exception):
    """Raised without disclosing any project information to an unknown user."""


class FounderAllowlist:
    def __init__(self, identities: list[FounderIdentity]) -> None:
        self._identities = {identity.telegram_user_id: identity for identity in identities}

    def authenticate(self, telegram_user_id: int) -> FounderIdentity:
        identity = self._identities.get(telegram_user_id)
        if identity is None or identity.status != "ACTIVE":
            raise AuthenticationError("access denied")
        return FounderIdentity(
            telegram_user_id=identity.telegram_user_id,
            founder_user_id=identity.founder_user_id,
            role=identity.role,
            permissions=identity.permissions,
            status=identity.status,
            last_verified=datetime.now(timezone.utc),
        )

    @staticmethod
    def require(identity: FounderIdentity, permission: str) -> None:
        if permission not in identity.permissions:
            raise AuthenticationError("permission denied")
