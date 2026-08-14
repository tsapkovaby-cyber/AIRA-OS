"""Ports implemented by AIRA Core and infrastructure, never by Telegram handlers."""

from typing import Protocol

from ..schemas.models import CallbackAction, FounderIdentity, FounderMessage, GatewayResponse


class AiraCoreGateway(Protocol):
    async def handle_message(self, message: FounderMessage, identity: FounderIdentity) -> GatewayResponse: ...

    async def handle_action(
        self, action: CallbackAction, identity: FounderIdentity, *, idempotency_key: str
    ) -> GatewayResponse: ...


class AuditSink(Protocol):
    async def emit(self, event: str, **attributes: object) -> None: ...
