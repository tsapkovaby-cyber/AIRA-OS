import asyncio

from backend.integrations.telegram.config import TelegramConfig
from backend.integrations.telegram.gateway import IncomingMessage, START, TECHNICAL_ERROR, TelegramGateway
from backend.telegram.schemas.models import GatewayResponse


class ConversationStub:
    def __init__(self):
        self.calls = []
        self.deleted = []

    async def respond(self, user_id, chat_id, message):
        self.calls.append((user_id, chat_id, message))
        return "legacy-response"

    def delete_user_data(self, user_id):
        self.deleted.append(user_id)
        return 1


class CoreStub:
    def __init__(self, fail=False):
        self.calls = []
        self.fail = fail

    async def handle_message(self, message, identity):
        self.calls.append((message, identity))
        if self.fail:
            raise RuntimeError("provider-secret-must-not-leak")
        return GatewayResponse("core-response", parse_mode=None)

    async def handle_action(self, action, identity, *, idempotency_key):
        raise AssertionError("callbacks are not migrated by this bridge yet")


def config():
    return TelegramConfig(
        "tg-secret", "ai-secret", 42, "test-model", None,
        "polling", None, None, 8080,
    )


def send(gateway, text, *, update_id=7, message_id=11, user_id=42, chat_id=99):
    return asyncio.run(gateway.handle(IncomingMessage(
        update_id=update_id,
        user_id=user_id,
        chat_id=chat_id,
        text=text,
        message_id=message_id,
    )))


def test_default_runtime_stays_on_existing_conversation_service():
    conversation = ConversationStub()
    gateway = TelegramGateway(config(), conversation)

    assert send(gateway, "hello") == "legacy-response"
    assert conversation.calls == [(42, 99, "hello")]


def test_optional_core_gateway_receives_transport_neutral_founder_message():
    conversation = ConversationStub()
    core = CoreStub()
    gateway = TelegramGateway(config(), conversation, core_gateway=core)

    assert send(gateway, "hello") == "core-response"
    assert conversation.calls == []
    assert len(core.calls) == 1

    message, identity = core.calls[0]
    assert message.telegram_update_id == 7
    assert message.telegram_message_id == 11
    assert message.founder_user_id == "42"
    assert message.conversation_id == "telegram:99"
    assert message.text == "hello"
    assert identity.telegram_user_id == 42
    assert identity.founder_user_id == "42"
    assert identity.role == "FOUNDER"


def test_gateway_commands_remain_local_during_migration():
    conversation = ConversationStub()
    core = CoreStub()
    gateway = TelegramGateway(config(), conversation, core_gateway=core)

    assert send(gateway, "/start") == START
    assert core.calls == []


def test_core_gateway_failure_is_sanitized_at_transport_boundary():
    conversation = ConversationStub()
    gateway = TelegramGateway(config(), conversation, core_gateway=CoreStub(fail=True))

    assert send(gateway, "hello") == TECHNICAL_ERROR
