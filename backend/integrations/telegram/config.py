"""Environment-only configuration for the Telegram MVP."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class TelegramConfig:
    bot_token: str
    openai_api_key: str
    founder_telegram_id: int | None
    model: str
    privacy_policy_url: str | None
    delivery_mode: str
    webhook_url: str | None
    webhook_port: int

    @classmethod
    def from_env(cls) -> "TelegramConfig":
        founder_value = os.getenv("AIRA_FOUNDER_TELEGRAM_ID", "").strip()
        try:
            founder_id = int(founder_value) if founder_value else None
        except ValueError as exc:
            raise ValueError("AIRA_FOUNDER_TELEGRAM_ID must be numeric") from exc

        mode = os.getenv("TELEGRAM_DELIVERY_MODE", "polling").strip().lower()
        if mode not in {"polling", "webhook"}:
            raise ValueError("TELEGRAM_DELIVERY_MODE must be polling or webhook")
        webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL", "").strip() or None
        if mode == "webhook" and not webhook_url:
            raise ValueError("TELEGRAM_WEBHOOK_URL is required in webhook mode")
        return cls(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
            openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
            founder_telegram_id=founder_id,
            model=os.getenv("AIRA_MODEL", "gpt-4.1-mini").strip(),
            privacy_policy_url=os.getenv("PRIVACY_POLICY_URL", "").strip() or None,
            delivery_mode=mode,
            webhook_url=webhook_url,
            webhook_port=int(os.getenv("PORT", "8080")),
        )

    def health(self) -> dict[str, bool | str]:
        return {
            "status": "running",
            "telegram_configured": bool(self.bot_token),
            "ai_provider_configured": bool(self.openai_api_key and self.model),
        }

    def validate_runtime(self) -> None:
        missing = []
        if not self.bot_token:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if self.founder_telegram_id is None:
            missing.append("AIRA_FOUNDER_TELEGRAM_ID")
        if missing:
            raise ValueError("Missing required configuration: " + ", ".join(missing))

