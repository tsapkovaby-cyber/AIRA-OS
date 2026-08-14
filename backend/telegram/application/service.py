"""Secure orchestration around the transport-to-Core boundary."""

import uuid

from ..adapter.founder import TelegramFounderAdapter
from ..auth.allowlist import AuthenticationError, FounderAllowlist
from ..callbacks.signer import CallbackSigner, InvalidCallback
from ..messaging.guards import DuplicateUpdate, IdempotencyStore, RateLimitExceeded, SlidingWindowRateLimiter
from ..schemas.models import Direction, FounderIdentity, FounderMessage, GatewayResponse, TelegramUpdate
from .ports import AiraCoreGateway, AuditSink


UNAVAILABLE = "AIRA OS временно недоступна.\n\nЯ не буду выполнять действие, пока связь не восстановлена."
STALE = "Это подтверждение устарело.\n\nЯ сформировала актуальное состояние."


class TelegramBotService:
    def __init__(
        self,
        adapter: TelegramFounderAdapter,
        core: AiraCoreGateway,
        audit: AuditSink,
        allowlist: FounderAllowlist,
        callbacks: CallbackSigner,
        *,
        idempotency: IdempotencyStore | None = None,
        rate_limiter: SlidingWindowRateLimiter | None = None,
    ) -> None:
        self._adapter = adapter
        self._core = core
        self._audit = audit
        self._allowlist = allowlist
        self._callbacks = callbacks
        self._idempotency = idempotency or IdempotencyStore()
        self._rate_limiter = rate_limiter or SlidingWindowRateLimiter()

    async def receive(self, raw_update: dict[str, object]) -> None:
        update = self._adapter.normalize(raw_update)
        try:
            self._idempotency.claim(f"telegram:update:{update.update_id}")
            self._rate_limiter.check(update.user_id)
            await self._audit.emit("TelegramMessageReceived", update_id=update.update_id)
            identity = self._allowlist.authenticate(update.user_id)
            await self._audit.emit("FounderAuthenticated", founder_user_id=identity.founder_user_id)
            if update.callback_data:
                response = await self._handle_callback(update, identity)
            else:
                message = FounderMessage(
                    message_id=str(uuid.uuid4()),
                    telegram_message_id=update.message_id,
                    telegram_update_id=update.update_id,
                    founder_user_id=identity.founder_user_id,
                    conversation_id=f"telegram:{update.chat_id}",
                    direction=Direction.INBOUND,
                    text=update.text,
                )
                response = await self._core.handle_message(message, identity)
            await self._adapter.send(update.chat_id, response)
        except AuthenticationError:
            await self._audit.emit("FounderAuthenticationFailed", telegram_user_id=update.user_id)
        except (DuplicateUpdate, RateLimitExceeded):
            return
        except InvalidCallback:
            if update.callback_query_id:
                await self._adapter.acknowledge_callback(update.callback_query_id, "Подтверждение устарело")
            await self._adapter.send(update.chat_id, GatewayResponse(STALE, parse_mode=None))
        except (ConnectionError, TimeoutError):
            await self._adapter.send(update.chat_id, GatewayResponse(UNAVAILABLE, parse_mode=None))

    async def _handle_callback(self, update: TelegramUpdate, identity: FounderIdentity) -> GatewayResponse:
        action = self._callbacks.verify(update.callback_data or "")
        permission = f"{action.object_type}:{action.action}"
        self._allowlist.require(identity, permission)
        response = await self._core.handle_action(
            action,
            identity,
            idempotency_key=f"telegram:callback:{update.update_id}",
        )
        if update.callback_query_id:
            await self._adapter.acknowledge_callback(update.callback_query_id)
        return response
