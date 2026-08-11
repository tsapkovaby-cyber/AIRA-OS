"""python-telegram-bot adapters. Business logic remains in TelegramGateway."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from .gateway import IncomingMessage, TECHNICAL_ERROR, TelegramGateway

LOGGER = logging.getLogger(__name__)


def make_message_handler(gateway: TelegramGateway):
    async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.effective_user or not update.effective_chat or not update.effective_message:
            return
        incoming = IncomingMessage(
            update_id=update.update_id,
            user_id=update.effective_user.id,
            chat_id=update.effective_chat.id,
            text=update.effective_message.text or "",
        )
        response = await gateway.handle(incoming)
        try:
            await update.effective_message.reply_text(response)
        except Exception as exc:
            # No retry containing message data and no token/error details in the log.
            LOGGER.error("telegram delivery failed category=%s", type(exc).__name__)

    return handle


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Catch unexpected adapter errors without exposing internals to the user."""
    LOGGER.error("telegram adapter error category=%s", type(context.error).__name__)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(TECHNICAL_ERROR)
        except Exception:
            LOGGER.error("telegram error notification failed")

