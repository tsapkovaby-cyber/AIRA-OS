import asyncio

import pytest

from backend.integrations.telegram.approvals import execute_signed_action, sign_approval_button
from backend.telegram.callbacks.signer import CallbackSigner, InvalidCallback
from backend.telegram.schemas.models import GatewayResponse


class FakeCore:
    def __init__(self):
        self.calls = []

    async def handle_action(self, action, identity, *, idempotency_key):
        self.calls.append((action, identity, idempotency_key))
        return GatewayResponse("approved", parse_mode=None)


def signer():
    return CallbackSigner(b"a" * 32, ttl_seconds=60)


def test_signed_approval_round_trip_uses_update_scoped_idempotency():
    core = FakeCore()
    button = sign_approval_button(
        signer(),
        label="Approve",
        action="approve",
        object_type="publication",
        object_id="42",
        version=3,
    )
    text = asyncio.run(
        execute_signed_action(
            signer=signer(),
            core=core,
            callback_data=button.callback_data,
            founder_telegram_id=123,
            update_id=99,
        )
    )
    assert text == "approved"
    action, identity, key = core.calls[0]
    assert action.action == "approve"
    assert action.object_type == "publication"
    assert action.object_id == "42"
    assert action.version == 3
    assert action.sensitive is True
    assert identity.telegram_user_id == 123
    assert key == "telegram:callback:99"
    assert len(button.callback_data.encode()) <= 64


def test_tampered_approval_is_rejected_before_core_execution():
    core = FakeCore()
    button = sign_approval_button(
        signer(), label="Approve", action="approve", object_type="publication", object_id="42"
    )
    tampered = button.callback_data[:-1] + ("A" if button.callback_data[-1] != "A" else "B")
    with pytest.raises(InvalidCallback):
        asyncio.run(
            execute_signed_action(
                signer=signer(), core=core, callback_data=tampered,
                founder_telegram_id=123, update_id=100,
            )
        )
    assert core.calls == []
