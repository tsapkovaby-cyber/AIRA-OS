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
        required = ("TELEGRAM_BOT_TOKEN", "TELEGRAM_WEBHOOK_SECRET", "AIRA_FOUNDER_TELEGRAM_ID")
        missing = [name for name in required if not os.environ.get(name)]
        if missing:
            raise ValueError("Missing required Telegram configuration: " + ", ".join(missing))
        mode = os.getenv("TELEGRAM_DELIVERY_MODE", "webhook").lower()
        if mode not in {"webhook", "long_polling"}:
            raise ValueError("TELEGRAM_DELIVERY_MODE must be webhook or long_polling")
        return cls(
            bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
            webhook_secret=os.environ["TELEGRAM_WEBHOOK_SECRET"],
            founder_id=int(os.environ["AIRA_FOUNDER_TELEGRAM_ID"]),
            bot_id=os.getenv("TELEGRAM_BOT_ID", ""),
            bot_username=os.getenv("TELEGRAM_BOT_USERNAME", ""),
            environment=os.getenv("AIRA_ENVIRONMENT", "development"),
            private_founder_mode=os.getenv("PRIVATE_FOUNDER_MODE", "true").lower() == "true",
            delivery_mode=mode,
            database_path=os.getenv("AIRA_DATABASE_PATH", "aira.db"),
            media_path=os.getenv("AIRA_MEDIA_PATH", "media"),
            max_media_bytes=int(os.getenv("TELEGRAM_MAX_MEDIA_BYTES", str(20 * 1024 * 1024))),
        )

    def redacted(self) -> dict[str, object]:
        return {
            "bot_token": "[REDACTED]",
            "webhook_secret": "[REDACTED]",
            "founder_id": self.founder_id,
            "environment": self.environment,
            "delivery_mode": self.delivery_mode,
        }
