import asyncio
import unittest

from backend.telegram.adapter import TelegramFounderAdapter
from backend.telegram.application.service import STALE, TelegramBotService
from backend.telegram.auth import FounderAllowlist
from backend.telegram.callbacks import CallbackSigner, InvalidCallback
from backend.telegram.messaging import DuplicateUpdate, IdempotencyStore, RateLimitExceeded, SlidingWindowRateLimiter
from backend.telegram.schemas.models import CallbackAction, FounderIdentity, GatewayResponse


class FakeClient:
    def __init__(self) -> None:
        self.messages = []
        self.answers = []

    async def send_message(self, **kwargs):
        self.messages.append(kwargs)

    async def answer_callback_query(self, **kwargs):
        self.answers.append(kwargs)


class FakeCore:
    def __init__(self) -> None:
        self.messages = []
        self.actions = []

    async def handle_message(self, message, identity):
        self.messages.append((message, identity))
        return GatewayResponse("core response", parse_mode=None)

    async def handle_action(self, action, identity, *, idempotency_key):
        self.actions.append((action, identity, idempotency_key))
        return GatewayResponse("action accepted", parse_mode=None)


class FakeAudit:
    def __init__(self) -> None:
        self.events = []

    async def emit(self, event, **attributes):
        self.events.append((event, attributes))


def update(update_id=1, user_id=42, *, callback_data=None):
    message = {"message_id": 7, "chat": {"id": 99}, "from": {"id": user_id}, "text": "/status"}
    value = {"update_id": update_id, "message": message}
    if callback_data is not None:
        value = {
            "update_id": update_id,
            "callback_query": {"id": "cb-1", "from": {"id": user_id}, "message": message, "data": callback_data},
        }
    return value


class CallbackSignerTests(unittest.TestCase):
    def setUp(self):
        self.signer = CallbackSigner(b"x" * 32, ttl_seconds=30)
        self.action = CallbackAction("approve", "content", "123", version=4, sensitive=True)

    def test_round_trip_and_expiry(self):
        token = self.signer.sign(self.action, now=100)
        self.assertLessEqual(len(token.encode()), 64)
        self.assertEqual(self.signer.verify(token, now=129), self.action)
        with self.assertRaises(InvalidCallback):
            self.signer.verify(token, now=131)

    def test_rejects_tampering(self):
        token = self.signer.sign(self.action, now=100)
        with self.assertRaises(InvalidCallback):
            self.signer.verify("A" + token[1:], now=100)


class GuardTests(unittest.TestCase):
    def test_idempotency_and_rate_limit(self):
        store = IdempotencyStore()
        store.claim("one")
        with self.assertRaises(DuplicateUpdate):
            store.claim("one")
        limiter = SlidingWindowRateLimiter(requests=1, window_seconds=10)
        limiter.check(42, now=1)
        with self.assertRaises(RateLimitExceeded):
            limiter.check(42, now=2)
        limiter.check(42, now=11)


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.client = FakeClient()
        self.core = FakeCore()
        self.audit = FakeAudit()
        self.signer = CallbackSigner(b"x" * 32)
        self.service = TelegramBotService(
            TelegramFounderAdapter(self.client),
            self.core,
            self.audit,
            FounderAllowlist(
                [FounderIdentity(42, "founder-1", "FOUNDER", frozenset({"content:approve"}))]
            ),
            self.signer,
        )

    def test_message_is_authenticated_normalized_and_delegated(self):
        asyncio.run(self.service.receive(update()))
        self.assertEqual(self.core.messages[0][0].text, "/status")
        self.assertEqual(self.core.messages[0][0].memory_policy, "FOUNDER_PRIVATE")
        self.assertEqual(self.client.messages[0]["text"], "core response")

    def test_unknown_user_gets_no_project_information(self):
        asyncio.run(self.service.receive(update(user_id=999)))
        self.assertEqual(self.client.messages, [])
        self.assertEqual(self.audit.events[-1][0], "FounderAuthenticationFailed")

    def test_signed_callback_is_delegated_to_core(self):
        token = self.signer.sign(CallbackAction("approve", "content", "123", version=4))
        asyncio.run(self.service.receive(update(callback_data=token)))
        self.assertEqual(self.core.actions[0][0].object_id, "123")
        self.assertEqual(self.core.actions[0][2], "telegram:callback:1")
        self.assertEqual(len(self.client.answers), 1)

    def test_invalid_callback_fails_closed(self):
        asyncio.run(self.service.receive(update(callback_data="invalid")))
        self.assertEqual(self.core.actions, [])
        self.assertEqual(self.client.messages[0]["text"], STALE)

    def test_redelivery_is_ignored(self):
        asyncio.run(self.service.receive(update()))
        asyncio.run(self.service.receive(update()))
        self.assertEqual(len(self.core.messages), 1)


if __name__ == "__main__":
    unittest.main()
