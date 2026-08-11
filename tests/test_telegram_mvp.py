import asyncio
import json
import logging
from urllib.request import urlopen

import pytest

from backend.integrations.telegram.config import TelegramConfig
from backend.integrations.telegram.conversation import AIRAConversationService, InMemoryConversationStore
from backend.integrations.telegram.gateway import IncomingMessage, START, TECHNICAL_ERROR, TelegramGateway
from backend.integrations.telegram.intelligence import AIRAIntelligenceProvider, AIRA_SYSTEM_INSTRUCTIONS


class FakeProvider(AIRAIntelligenceProvider):
    def __init__(self, fail=False): self.calls, self.fail = [], fail
    async def generate_response(self, messages):
        self.calls.append(list(messages))
        if self.fail: raise RuntimeError("secret-token-must-not-leak")
        return "Привет! Рада тебя слышать."


def config(founder=42, privacy=None):
    return TelegramConfig("tg-secret", "ai-secret", founder, "test-model", privacy, "polling", None, None, 8080)


def gateway(provider=None, founder=42, privacy=None):
    provider = provider or FakeProvider()
    service = AIRAConversationService(provider, InMemoryConversationStore())
    return TelegramGateway(config(founder, privacy), service), provider


def send(gw, text, user=42, chat=10, update=1):
    return asyncio.run(gw.handle(IncomingMessage(update, user, chat, text)))


def test_start_and_founder_authentication():
    gw, _ = gateway()
    assert send(gw, "/start") == START
    assert "ограничен" in send(gw, "/start", user=99)


def test_text_conversation_is_russian_and_identity_is_canonical():
    gw, provider = gateway()
    assert "Привет" in send(gw, "Аира, привет")
    assert provider.calls[0][-1]["content"] == "Аира, привет"
    assert "виртуальная AI-личность" in AIRA_SYSTEM_INSTRUCTIONS
    assert "русском" in AIRA_SYSTEM_INSTRUCTIONS
    assert "биологического человека" in AIRA_SYSTEM_INSTRUCTIONS


def test_memory_isolation_and_context():
    gw, provider = gateway()
    send(gw, "первое", chat=10)
    send(gw, "второе", chat=10)
    assert [m["content"] for m in provider.calls[1]] == ["первое", "Привет! Рада тебя слышать.", "второе"]
    send(gw, "другой чат", chat=11)
    assert len(provider.calls[2]) == 1
    assert "ограничен" in send(gw, "чужой", user=99)
    assert len(provider.calls) == 3


def test_privacy_and_delete_data():
    gw, provider = gateway(privacy="https://example.test/privacy")
    assert "https://example.test/privacy" in send(gw, "/privacy")
    send(gw, "remember")
    assert "Локальная история" in send(gw, "/delete_my_data")
    send(gw, "fresh")
    assert len(provider.calls[-1]) == 1


def test_setup_id_only_when_unconfigured():
    gw, _ = gateway(founder=None)
    assert "42" in send(gw, "/start")
    gw, _ = gateway(founder=42)
    assert "Telegram ID" not in send(gw, "/start")


def test_provider_failure_is_sanitized(caplog):
    gw, _ = gateway(FakeProvider(fail=True))
    with caplog.at_level(logging.INFO):
        assert send(gw, "hello") == TECHNICAL_ERROR
    combined = caplog.text
    assert "tg-secret" not in combined and "ai-secret" not in combined
    assert "secret-token-must-not-leak" not in TECHNICAL_ERROR


def test_health_has_no_secrets():
    gw, _ = gateway()
    response = send(gw, "/health")
    assert "готов" in response
    assert "secret" not in response


def test_render_health_endpoint_is_secret_free():
    from backend.integrations.telegram.health import start_health_server

    server = start_health_server(config(), 0)
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/health") as response:
            health = json.load(response)
        assert health == {
            "status": "running",
            "telegram_configured": True,
            "ai_provider_configured": True,
            "delivery_mode": "polling",
        }
        assert "secret" not in json.dumps(health)
    finally:
        server.shutdown()
        server.server_close()


def test_bootstrap_configuration_allows_missing_founder_id(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("OPENAI_API_KEY", "key")
    monkeypatch.delenv("AIRA_FOUNDER_TELEGRAM_ID", raising=False)
    TelegramConfig.from_env().validate_runtime()


def test_webhook_requires_secret(monkeypatch):
    monkeypatch.setenv("TELEGRAM_DELIVERY_MODE", "webhook")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_URL", "https://example.test/telegram")
    monkeypatch.delenv("TELEGRAM_WEBHOOK_SECRET", raising=False)
    with pytest.raises(ValueError, match="TELEGRAM_WEBHOOK_SECRET"):
        TelegramConfig.from_env()


class FailedTelegramMessage:
    text = "hi"
    async def reply_text(self, value): raise ConnectionError("telegram-token-secret")


def test_telegram_failure_is_swallowed(caplog):
    pytest.importorskip("telegram")
    from backend.integrations.telegram.handlers import make_message_handler
    class Update:
        update_id = 1
        effective_user = type("U", (), {"id": 42})()
        effective_chat = type("C", (), {"id": 10})()
        effective_message = FailedTelegramMessage()
    gw, _ = gateway()
    with caplog.at_level(logging.ERROR):
        asyncio.run(make_message_handler(gw)(Update(), None))
    assert "telegram delivery failed" in caplog.text
    assert "telegram-token-secret" not in caplog.text
