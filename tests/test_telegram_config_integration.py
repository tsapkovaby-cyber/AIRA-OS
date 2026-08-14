import pytest

from aira_os.telegram.config import TelegramConfig


def _base_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("AIRA_FOUNDER_TELEGRAM_ID", "42")
    monkeypatch.delenv("TELEGRAM_WEBHOOK_SECRET", raising=False)
    monkeypatch.delenv("TELEGRAM_DELIVERY_MODE", raising=False)


def test_polling_alias_matches_live_mvp_without_webhook_secret(monkeypatch):
    _base_env(monkeypatch)
    monkeypatch.setenv("TELEGRAM_DELIVERY_MODE", "polling")

    config = TelegramConfig.from_env()

    assert config.delivery_mode == "long_polling"
    assert config.webhook_secret == ""


def test_long_polling_does_not_require_webhook_secret(monkeypatch):
    _base_env(monkeypatch)
    monkeypatch.setenv("TELEGRAM_DELIVERY_MODE", "long_polling")

    config = TelegramConfig.from_env()

    assert config.delivery_mode == "long_polling"


def test_webhook_requires_webhook_secret(monkeypatch):
    _base_env(monkeypatch)
    monkeypatch.setenv("TELEGRAM_DELIVERY_MODE", "webhook")

    with pytest.raises(ValueError, match="TELEGRAM_WEBHOOK_SECRET"):
        TelegramConfig.from_env()


def test_webhook_accepts_secret(monkeypatch):
    _base_env(monkeypatch)
    monkeypatch.setenv("TELEGRAM_DELIVERY_MODE", "webhook")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "hook-secret")

    config = TelegramConfig.from_env()

    assert config.delivery_mode == "webhook"
    assert config.webhook_secret == "hook-secret"
