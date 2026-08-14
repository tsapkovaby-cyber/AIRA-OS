"""Migration bridge from the live Telegram MVP to the canonical Core gateway contract.

The Railway entry point does not enable this bridge yet.  It exists so the live
python-telegram-bot transport can be migrated behind ``backend.telegram``
without starting a second Telegram process.
"""

from __future__ import annotations

import uuid

from backend.telegram.application.ports import AiraCoreGateway
from backend.telegram.schemas.models import Direction, FounderIdentity, FounderMessage


def founder_identity(telegram_user_id: int) -> FounderIdentity:
    """Build the private-Founder identity used at the Telegram/Core boundary."""
    return FounderIdentity(
        telegram_user_id=telegram_user_id,
        founder_user_id=str(telegram_user_id),
        role="FOUNDER",
        permissions=frozenset({"chat"}),
    )


def founder_message(
    *,
    update_id: int,
    message_id: int,
    user_id: int,
    chat_id: int,
    text: str,
) -> FounderMessage:
    """Normalize the live MVP message into the canonical transport-neutral model."""
    return FounderMessage(
        message_id=str(uuid.uuid4()),
        telegram_message_id=message_id,
        telegram_update_id=update_id,
        founder_user_id=str(user_id),
        conversation_id=f"telegram:{chat_id}",
        direction=Direction.INBOUND,
        text=text,
    )


__all__ = ["AiraCoreGateway", "founder_identity", "founder_message"]
