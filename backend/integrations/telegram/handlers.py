"""python-telegram-bot adapters. Business logic remains in TelegramGateway."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from backend.telegram.application.ports import AiraCoreGateway
from backend.telegram.callbacks.signer import CallbackSigner, InvalidCallback

from .approvals import STALE_APPROVAL, execute_signed_action
from .auth import Role
from .gateway import DENIED, IncomingMessage, TECHNICAL_ERROR, TelegramGateway

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
            message_id=getattr(update.effective_message, "message_id", 0),
        )
        response = await gateway.handle(incoming)
        try:
            await update.effective_message.reply_text(response)
        except Exception as exc:
            # No retry containing message data and no token/error details in the log.
            LOGGER.error("telegram delivery failed category=%s", type(exc).__name__)

    return handle


def make_callback_handler(
    gateway: TelegramGateway,
    *,
    signer: CallbackSigner,
    core: AiraCoreGateway,
):
    """Handle signed approval callbacks in the existing bot process only."""
    async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        user = update.effective_user
        if query is None or user is None:
            return
        try:
            if gateway.auth.role_for(user.id) is not Role.FOUNDER:
                await query.answer(DENIED, show_alert=True)
                return
            text = await execute_signed_action(
                signer=signer,
                core=core,
                callback_data=query.data or "",
                founder_telegram_id=user.id,
                update_id=update.update_id,
            )
            await query.answer()
            if query.message is not None:
                await query.message.reply_text(text)
        except InvalidCallback:
            await query.answer(STALE_APPROVAL, show_alert=True)
        except Exception as exc:
            LOGGER.error("telegram callback failed update_id=%s category=%s", update.update_id, type(exc).__name__)
            try:
                await query.answer(TECHNICAL_ERROR, show_alert=True)
            except Exception:
                LOGGER.error("telegram callback error notification failed")

    return handle


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Catch unexpected adapter errors without exposing internals to the user."""
    LOGGER.error("telegram adapter error category=%s", type(context.error).__name__)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(TECHNICAL_ERROR)
        except Exception:
            LOGGER.error("telegram error notification failed")
