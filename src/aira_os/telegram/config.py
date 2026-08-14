from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class TelegramConfig:
    bot_token: str
    webhook_secret: str
    founder_id: int
    bot_id: str = ""
    bot_username: str = ""
    environment: str = "development"
    private_founder_mode: bool = True
    delivery_mode: str = "webhook"
    database_path: str = "aira.db"
    media_path: str = "media"
    max_media_bytes: int = 20 * 1024 * 1024

    @classmethod
    def from_env(cls) -> "TelegramConfig":
        required = ("TELEGRAM_BOT_TOKEN", "AIRA_FOUNDER_TELEGRAM_ID")
        missing = [name for name in required if not os.environ.get(name)]
        if missing:
            raise ValueError("Missing required Telegram configuration: " + ", ".join(missing))

        raw_mode = os.getenv("TELEGRAM_DELIVERY_MODE", "webhook").lower()
        # The live MVP uses "polling" while Sprint 022 originally used
        # "long_polling". Treat them as the same transport mode so one
        # deployment environment cannot accidentally configure two meanings.
        mode = "long_polling" if raw_mode == "polling" else raw_mode
        if mode not in {"webhook", "long_polling"}:
            raise ValueError(
                "TELEGRAM_DELIVERY_MODE must be webhook, polling, or long_polling"
            )

        webhook_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
        if mode == "webhook" and not webhook_secret:
            raise ValueError(
                "Missing required Telegram configuration for webhook mode: "
                "TELEGRAM_WEBHOOK_SECRET"
            )

        return cls(
            bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
            webhook_secret=webhook_secret,
            founder_id=int(os.environ["AIRA_FOUNDER_TELEGRAM_ID"]),
            bot_id=os.getenv("TELEGRAM_BOT_ID", ""),
            bot_username=os.getenv("TELEGRAM_BOT_USERNAME", ""),
            environment=os.getenv("AIRA_ENVIRONMENT", "development"),
            private_founder_mode=os.getenv("PRIVATE_FOUNDER_MODE", "true").lower() == "true",
            delivery_mode=mode,
            database_path=os.getenv("AIRA_DATABASE_PATH", "aira.db"),
            media_path=os.getenv("AIRA_MEDIA_PATH", "media"),
            max_media_bytes=int(
                os.getenv("TELEGRAM_MAX_MEDIA_BYTES", str(20 * 1024 * 1024))
            ),
        )

    def redacted(self) -> dict[str, object]:
        return {
            "bot_token": "[REDACTED]",
            "webhook_secret": "[REDACTED]",
            "founder_id": self.founder_id,
            "environment": self.environment,
            "delivery_mode": self.delivery_mode,
        }
