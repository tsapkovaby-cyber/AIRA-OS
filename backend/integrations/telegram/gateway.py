"""Telegram gateway: authorization and transport-neutral request handling."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import time

from backend.education.telegram import TelegramEducationAdapter

from .auth import FounderAuthenticator, Role
from .config import TelegramConfig
from .conversation import AIRAConversationService

LOGGER = logging.getLogger(__name__)
TECHNICAL_ERROR = "У меня возникла техническая ошибка.\nПопробуй отправить сообщение ещё раз."
DENIED = "Сейчас это приватная тестовая версия AIRA. Доступ к диалогу ограничен."
START = "Привет 💜\nЯ AIRA.\n\nЯ уже на связи.\n\nМожем просто поговорить или начать\nработать над нашим проектом."
HELP = "Я умею вести диалог и проводить языковые занятия. Команды: /learn, /privacy, /delete_my_data, /health."


@dataclass(frozen=True)
class IncomingMessage:
    update_id: int
    user_id: int
    chat_id: int
    text: str


def safe_chat_id(chat_id: int) -> str:
    value = str(abs(chat_id))
    return f"…{value[-4:]}" if len(value) > 4 else "…" + value


class TelegramGateway:
    def __init__(
        self,
        config: TelegramConfig,
        conversation: AIRAConversationService,
        education: TelegramEducationAdapter | None = None,
    ):
        self.config = config
        self.conversation = conversation
        self.education = education
        self.auth = FounderAuthenticator(config.founder_telegram_id)

    async def handle(self, incoming: IncomingMessage) -> str:
        started = time.monotonic()
        status = "ok"
        category = "none"
        try:
            identity = self.auth.setup_identity_message(incoming.user_id)
            if identity:
                return identity
            if self.auth.role_for(incoming.user_id) is not Role.FOUNDER:
                return DENIED
            command = incoming.text.strip().split(maxsplit=1)[0].lower()
            if command == "/start":
                return START
            if command == "/help":
                return HELP
            if command == "/learn":
                if not self.education:
                    return "AIRA Academy is not configured."
                return self.education.handle_learn(str(incoming.user_id))
            if command == "/privacy":
                if self.config.privacy_policy_url:
                    return f"Политика конфиденциальности: {self.config.privacy_policy_url}"
                return ("Это приватное тестирование. Недавние сообщения временно хранятся "
                        "в памяти процесса для контекста и передаются AI-провайдеру для ответа.")
            if command == "/delete_my_data":
                self.conversation.delete_user_data(incoming.user_id)
                if self.education:
                    self.education.api.repository.delete_for_platform_user(str(incoming.user_id))
                return ("Локальная история ваших бесед удалена. Это подтверждение относится "
                        "только к данным, хранившимся в AIRA OS, а не у внешних провайдеров.")
            if command == "/health":
                health = self.config.health()
                return (f"AIRA OS: {health['status']}; Telegram: "
                        f"{'готов' if health['telegram_configured'] else 'не настроен'}; AI: "
                        f"{'готов' if health['ai_provider_configured'] else 'не настроен'}.")
            if command.startswith("/"):
                return "Неизвестная команда. Доступные команды перечислены в /help."
            return await self.conversation.respond(
                incoming.user_id, incoming.chat_id, incoming.text
            )
        except Exception as exc:  # transport boundary: sanitize every provider failure
            status, category = "error", type(exc).__name__
            LOGGER.error(
                "telegram processing failed update_id=%s chat=%s category=%s",
                incoming.update_id, safe_chat_id(incoming.chat_id), category,
            )
            return TECHNICAL_ERROR
        finally:
            LOGGER.info(
                "telegram update update_id=%s chat=%s status=%s latency_ms=%d error_category=%s",
                incoming.update_id, safe_chat_id(incoming.chat_id), status,
                int((time.monotonic() - started) * 1000), category,
            )
