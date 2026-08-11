"""Executable entry point for polling or webhook delivery (never both)."""

from __future__ import annotations

import logging

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from .config import TelegramConfig
from .conversation import AIRAConversationService, InMemoryConversationStore
from .gateway import TelegramGateway
from .handlers import error_handler, make_message_handler
from .health import start_health_server
from .intelligence import OpenAIResponsesProvider
from backend.education import EducationAPI
from backend.education.telegram import TelegramEducationAdapter


def build_application(config: TelegramConfig) -> Application:
    provider = OpenAIResponsesProvider(config.openai_api_key, config.model)
    conversation = AIRAConversationService(provider, InMemoryConversationStore())
    gateway = TelegramGateway(config, conversation, TelegramEducationAdapter(EducationAPI()))
    app = Application.builder().token(config.bot_token).build()
    handler = make_message_handler(gateway)
    for command in ("start", "help", "learn", "privacy", "delete_my_data", "health"):
        app.add_handler(CommandHandler(command, handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
    app.add_error_handler(error_handler)
    return app


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    config = TelegramConfig.from_env()
    config.validate_runtime()
    app = build_application(config)
    if config.delivery_mode == "polling":
        start_health_server(config, config.webhook_port)
        app.run_polling(drop_pending_updates=False)
    else:
        assert config.webhook_url
        app.run_webhook(
            listen="0.0.0.0", port=config.webhook_port,
            url_path="telegram",
            webhook_url=config.webhook_url,
            secret_token=config.webhook_secret,
        )


if __name__ == "__main__":
    main()
