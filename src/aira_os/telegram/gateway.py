from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib import parse, request
from .config import TelegramConfig
from .models import MessageType, TelegramMessage


class TelegramGateway:
    def __init__(self, config: TelegramConfig, transport=None):
        self.config = config
        self.transport = transport or self._request

    def _request(self, method: str, data: dict) -> dict:
        # Token remains only in the transport URL and is never logged.
        url = f"https://api.telegram.org/bot{self.config.bot_token}/{method}"
        body = parse.urlencode(data).encode()
        with request.urlopen(request.Request(url, data=body), timeout=30) as response:
            return json.loads(response.read())

    def normalize(self, update: dict) -> TelegramMessage:
        update_id = int(update["update_id"])
        if "callback_query" in update:
            cb = update["callback_query"]; origin = cb.get("message", {})
            return TelegramMessage(int(origin.get("message_id", 0)), int(origin.get("chat", {}).get("id", cb["from"]["id"])), int(cb["from"]["id"]), MessageType.BUTTON_CALLBACK, telegram_update_id=update_id, callback_data=cb.get("data", ""))
        msg = update.get("message") or update.get("edited_message")
        if not msg: raise ValueError("Unsupported Telegram update")
        text = msg.get("text") or msg.get("caption") or ""
        kind, refs = MessageType.TEXT, []
        for key, message_type in (("voice",MessageType.VOICE),("photo",MessageType.PHOTO),("video",MessageType.VIDEO),("document",MessageType.DOCUMENT),("audio",MessageType.AUDIO)):
            if key in msg:
                kind = message_type
                value = msg[key][-1] if key == "photo" else msg[key]
                refs = [{k: value.get(k) for k in ("file_id","file_unique_id","file_size","mime_type","file_name") if value.get(k) is not None}]
                break
        if text.startswith("/"): kind = MessageType.COMMAND
        elif msg.get("reply_to_message") and kind == MessageType.TEXT: kind = MessageType.REPLY
        reply = msg.get("reply_to_message")
        reply_context = ({"message_id": reply.get("message_id"), "text": reply.get("text") or reply.get("caption", "")} if reply else None)
        return TelegramMessage(int(msg["message_id"]), int(msg["chat"]["id"]), int(msg["from"]["id"]), kind, text, refs, reply_context, int(msg.get("date",0)), update_id)

    def send_text(self, chat_id: int, text: str, buttons: list[list[dict]] | None = None):
        data: dict[str, Any] = {"chat_id": chat_id, "text": text}
        if buttons: data["reply_markup"] = json.dumps({"inline_keyboard": buttons})
        return self.transport("sendMessage", data)

    def send_typing(self, chat_id: int): return self.transport("sendChatAction", {"chat_id":chat_id,"action":"typing"})
    def send_voice(self, chat_id: int, file_path: str): return self.transport("sendVoice", {"chat_id":chat_id,"voice":file_path})
    def answer_callback(self, callback_id: str, text: str): return self.transport("answerCallbackQuery", {"callback_query_id":callback_id,"text":text})

    def download_media(self, ref: dict) -> str:
        size = int(ref.get("file_size", 0))
        if size > self.config.max_media_bytes: raise ValueError("Media exceeds configured size limit")
        info = self.transport("getFile", {"file_id": ref["file_id"]})
        remote = info["result"]["file_path"]
        suffix = Path(remote).suffix
        destination = Path(self.config.media_path) / f"{ref.get('file_unique_id', ref['file_id'])}{suffix}"
        destination.parent.mkdir(parents=True, exist_ok=True)
        if hasattr(self.transport, "download"):
            self.transport.download(remote, destination)
        else:
            url = f"https://api.telegram.org/file/bot{self.config.bot_token}/{remote}"
            request.urlretrieve(url, destination)
        return str(destination)
