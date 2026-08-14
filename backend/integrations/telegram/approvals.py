"""Approval/callback bridge for the single live Telegram transport.

This module deliberately contains no polling/webhook startup code. It lets the
existing python-telegram-bot process render and verify canonical signed actions
from ``backend.telegram`` while AIRA Core remains behind the gateway port.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.telegram.application.ports import AiraCoreGateway
from backend.telegram.callbacks.signer import CallbackSigner, InvalidCallback
from backend.telegram.schemas.models import Button, CallbackAction

from .core_bridge import founder_identity


STALE_APPROVAL = "Это подтверждение устарело. Запроси действие ещё раз."
DENIED_APPROVAL = "Подтверждение доступно только основателю AIRA."


@dataclass(frozen=True, slots=True)
class ApprovalButton:
    label: str
    callback_data: str


def sign_approval_button(
    signer: CallbackSigner,
    *,
    label: str,
    action: str,
    object_type: str,
    object_id: str,
    version: int | None = None,
    sensitive: bool = True,
) -> ApprovalButton:
    """Create a short-lived tamper-evident Telegram approval button."""
    callback_data = signer.sign(
        CallbackAction(
            action=action,
            object_type=object_type,
            object_id=object_id,
            version=version,
            sensitive=sensitive,
        )
    )
    return ApprovalButton(label=label, callback_data=callback_data)


def canonical_button(button: ApprovalButton) -> Button:
    return Button(label=button.label, callback_data=button.callback_data)


async def execute_signed_action(
    *,
    signer: CallbackSigner,
    core: AiraCoreGateway,
    callback_data: str,
    founder_telegram_id: int,
    update_id: int,
) -> str:
    """Verify and execute one callback with an update-scoped idempotency key."""
    action = signer.verify(callback_data)
    response = await core.handle_action(
        action,
        founder_identity(founder_telegram_id),
        idempotency_key=f"telegram:callback:{update_id}",
    )
    return response.text


__all__ = [
    "ApprovalButton",
    "DENIED_APPROVAL",
    "InvalidCallback",
    "STALE_APPROVAL",
    "canonical_button",
    "execute_signed_action",
    "sign_approval_button",
]
