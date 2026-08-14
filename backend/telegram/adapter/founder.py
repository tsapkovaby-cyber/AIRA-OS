"""Telegram transport adapter. It deliberately contains no AIRA business rules."""

from typing import Any, Protocol

from ..schemas.models import Button, GatewayResponse, TelegramUpdate


class TelegramClient(Protocol):
    async def send_message(self, **kwargs: Any) -> Any: ...

    async def answer_callback_query(self, **kwargs: Any) -> Any: ...


class TelegramFounderAdapter:
    def __init__(self, client: TelegramClient) -> None:
        self._client = client

    def normalize(self, raw: dict[str, Any]) -> TelegramUpdate:
        callback = raw.get("callback_query")
        message = (callback or {}).get("message") or raw.get("message") or {}
        sender = (callback or {}).get("from") or message.get("from") or {}
        return TelegramUpdate(
            update_id=int(raw["update_id"]),
            user_id=int(sender["id"]),
            chat_id=int(message["chat"]["id"]),
            message_id=int(message["message_id"]),
            text=str(message.get("text", "")),
            callback_query_id=(callback or {}).get("id"),
            callback_data=(callback or {}).get("data"),
            raw=raw,
        )

    async def send(self, chat_id: int, response: GatewayResponse) -> None:
        keyboard = [[self._button(item) for item in row] for row in response.buttons]
        await self._client.send_message(
            chat_id=chat_id,
            text=response.text,
            parse_mode=response.parse_mode,
            reply_markup={"inline_keyboard": keyboard} if keyboard else None,
        )

    async def acknowledge_callback(self, callback_query_id: str, text: str = "") -> None:
        await self._client.answer_callback_query(callback_query_id=callback_query_id, text=text)

    @staticmethod
    def _button(button: Button) -> dict[str, str]:
        result = {"text": button.label}
        if button.callback_data:
            result["callback_data"] = button.callback_data
        if button.url:
            result["url"] = button.url
        return result
