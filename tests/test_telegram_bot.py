from dataclasses import replace
from types import SimpleNamespace

import pytest

import logging

from backend.integrations.telegram.bot import SecretRedactionFilter, Settings, TelegramGateway
from backend.integrations.telegram.memory import ProcessLocalConversationMemory


class FakeMessage:
    def __init__(self, text=""):
        self.text, self.replies = text, []
    async def reply_text(self, text):
        self.replies.append(text)


class FakeIntelligence:
    async def reply(self, history, message):
        return "фиолетовый" if history else "Привет"


def settings(**changes):
    base = Settings("token", "key", 42, "model", None, "polling", None, None, 8080)
    return replace(base, **changes)


def gateway(config):
    return TelegramGateway(config, ProcessLocalConversationMemory(), FakeIntelligence())


def update(user_id=42, text="hello", username="founder", chat_type="private"):
    return SimpleNamespace(effective_user=SimpleNamespace(id=user_id, username=username), effective_chat=SimpleNamespace(type=chat_type), message=FakeMessage(text))


@pytest.mark.asyncio
async def test_numeric_id_authentication_ignores_username():
    bot = gateway(settings())
    forged = update(user_id=99, username="founder")
    await bot.message(forged, None)
    assert forged.message.replies == []


@pytest.mark.asyncio
async def test_bootstrap_only_when_founder_unset_and_private():
    bootstrap = gateway(settings(founder_id=None))
    first = update(user_id=777)
    await bootstrap.start(first, None)
    assert "777" in first.message.replies[0]
    configured = gateway(settings())
    second = update()
    await configured.start(second, None)
    assert "42" not in second.message.replies[0]


@pytest.mark.asyncio
async def test_memory_context_and_local_deletion_notice():
    bot = gateway(settings())
    first = update(text="remember")
    await bot.message(first, None)
    second = update(text="what?")
    await bot.message(second, None)
    assert second.message.replies == ["фиолетовый"]
    deletion = update()
    await bot.delete_my_data(deletion, None)
    assert "Telegram" in deletion.message.replies[0]
    assert bot.memory.history(42) == []


def test_health_contains_no_secret_values():
    data = settings().health()
    rendered = str(data)
    assert data == {"status": "running", "telegram_configured": True, "ai_provider_configured": True, "delivery_mode": "polling"}
    assert "token" not in rendered and "key" not in rendered


def test_webhook_requires_https_and_secret():
    with pytest.raises(ValueError, match="HTTPS"):
        settings(delivery_mode="webhook", webhook_url="http://example.test").validate()


def test_log_filter_redacts_credentials():
    record = logging.LogRecord("test", logging.ERROR, "", 0, "failed token=%s", ("sensitive",), None)
    SecretRedactionFilter(("sensitive",)).filter(record)
    assert record.getMessage() == "failed token=[REDACTED]"
