"""Executable entry point for polling or webhook delivery (never both)."""

from __future__ import annotations

import logging

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from .config import TelegramConfig
from .conversation import AIRAConversationService, InMemoryConversationStore
from .gateway import TelegramGateway
from .handlers import error_handler, make_message_handler
from .intelligence import OpenAIResponsesProvider


def build_application(config: TelegramConfig) -> Application:
    provider = OpenAIResponsesProvider(config.openai_api_key, config.model)
    conversation = AIRAConversationService(provider, InMemoryConversationStore())
    gateway = TelegramGateway(config, conversation)
    app = Application.builder().token(config.bot_token).build()
    handler = make_message_handler(gateway)
    for command in ("start", "help", "privacy", "delete_my_data", "health"):
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
        app.run_polling(drop_pending_updates=False)
    else:
        assert config.webhook_url
        app.run_webhook(
            listen="0.0.0.0", port=config.webhook_port,
            webhook_url=config.webhook_url,
        )


if __name__ == "__main__":
    main()

