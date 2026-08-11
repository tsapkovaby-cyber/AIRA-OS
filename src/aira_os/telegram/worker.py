from __future__ import annotations

import json
import logging
from .audit import Audit
from .models import MessageType


class TelegramWorker:
    def __init__(self, store, gateway, security, core, perception=None, speech=None, memory=None, audit=None):
        self.store, self.gateway, self.security, self.core = store, gateway, security, core
        self.perception, self.speech, self.memory = perception, speech, memory
        self.audit = audit or Audit(); self.log = logging.getLogger(__name__)

    def run_once(self) -> bool:
        row = self.store.next_update()
        if not row: return False
        update_id = row["update_id"]
        try:
            update = json.loads(row["payload"]); message = self.gateway.normalize(update)
            self.audit.emit("TelegramMessageReceived", update_id=update_id, user_id=message.user_id, type=message.type)
            self._process(message, update)
            self.store.finish(update_id); self.audit.emit("TelegramMessageProcessed", update_id=update_id)
        except Exception as exc:
            self.store.finish(update_id, type(exc).__name__)
            self.audit.emit("TelegramError", update_id=update_id, error_type=type(exc).__name__)
            try: self.gateway.send_text(message.chat_id, "Не получилось обработать сообщение. Я сохранила ошибку. Попробовать ещё раз?")
            except Exception: pass
        return True

    def _process(self, message, update):
        if not self.security.rate_limit(message.user_id):
            self.gateway.send_text(message.chat_id, "Слишком много сообщений. Попробуйте чуть позже."); return
        if not self.security.authorize(message.user_id):
            self.audit.emit("TelegramAuthFailed", user_id=message.user_id)
            self.gateway.send_text(message.chat_id, "Этот бот сейчас доступен только владельцу."); return
        if message.type == MessageType.BUTTON_CALLBACK:
            return self._callback(message, update)
        session = self.store.session(message.chat_id, message.user_id)
        if message.type == MessageType.COMMAND:
            return self._command(message, session)
        self.gateway.send_typing(message.chat_id)
        text = message.text
        if message.media_references:
            path = self.gateway.download_media(message.media_references[0])
            self.audit.emit("TelegramMediaReceived", update_id=message.telegram_update_id, type=message.type)
            if message.type in {MessageType.VOICE, MessageType.AUDIO}:
                if not self.speech: raise RuntimeError("Speech engine unavailable")
                text = self.speech.transcribe(path)
            else:
                if not self.perception: raise RuntimeError("Perception unavailable")
                text = self.perception.understand(path, message.type.value, message.text)
        message.text = text
        history = self.memory.recent(session.session_id) if self.memory else self.store.history(session.session_id)
        self.store.add_history(session.session_id, "user", text)
        answer = self.core.respond(message, session, history)
        self.store.add_history(session.session_id, "assistant", answer)
        if self.memory:
            self.memory.consider(session.session_id, "user", text); self.memory.consider(session.session_id, "assistant", answer)
        self.gateway.send_text(message.chat_id, answer); self.audit.emit("TelegramResponseSent", chat_id=message.chat_id)

    def _command(self, message, session):
        command, _, arg = message.text.partition(" "); command = command.split("@")[0].lower()
        self.audit.emit("TelegramCommandReceived", command=command, user_id=message.user_id)
        if command == "/start": answer = "Привет 💜\nЯ здесь. Режим основателя подтверждён. Что будем делать?"
        elif command == "/help": answer = "Команды: /status, /tasks, /memory, /research, /voice, /approvals, /settings, /cancel, /stop"
        elif command == "/status":
            s=self.core.status(); answer=f"AIRA: {s.get('status','OK')}\nАктивные модули: {', '.join(s.get('modules',[])) or '—'}\nОжидают подтверждения: {len(self.store.pending(message.user_id))}\nАвтономность: {'пауза' if self.store.paused() else 'включена'}"
        elif command == "/tasks":
            tasks=self.core.tasks(); answer="Задачи:\n" + ("\n".join(f"• {x.get('status')}: {x.get('title')}" for x in tasks) or "Нет активных задач.")
        elif command == "/research":
            answer = "Укажите тему после /research." if not arg else ("Автономность приостановлена." if self.store.paused() else self.core.research(arg, session))
        elif command == "/approvals":
            items=self.store.pending(message.user_id); answer="Ожидают подтверждения:\n"+("\n".join(f"• {x['proposal_id']}: {x['action']}" for x in items) or "Нет запросов.")
        elif command in {"/cancel","/stop"}: answer = "Текущая операция остановлена." if self.core.cancel(session) else "Нет активной отменяемой операции."
        elif command == "/voice": answer = "Голосовые ответы настраиваются: off, on_voice, always, manual. По умолчанию: off."
        elif command == "/memory": answer = "Память подключена. Я сохраняю только сведения, прошедшие политику памяти."
        elif command == "/settings": answer = "Настройки: PAUSE_AUTONOMY. Используйте /pause или /resume."
        elif command == "/pause": self.store.set_paused(True); answer = "Автономные действия приостановлены. Разговор остаётся доступен."
        elif command == "/resume": self.store.set_paused(False); answer = "Автономные действия возобновлены."
        else: answer = "Не знаю эту команду. Используйте /help."
        self.gateway.send_text(message.chat_id, answer)

    def _callback(self, message, update):
        parts = message.callback_data.split(":", 2)
        if len(parts) != 3 or parts[0] != "proposal" or parts[2] not in {"approve","reject"}:
            self.gateway.send_text(message.chat_id, "Некорректное действие."); return
        if not self.security.is_founder(message.user_id):
            self.audit.emit("TelegramAuthFailed", user_id=message.user_id); return
        status = "APPROVED" if parts[2] == "approve" else "REJECTED"
        changed = self.store.decide(parts[1], message.user_id, status)
        event = "TelegramApprovalGranted" if status == "APPROVED" else "TelegramApprovalRejected"
        if changed: self.audit.emit(event, proposal_id=parts[1], user_id=message.user_id)
        callback_id = update.get("callback_query", {}).get("id", "")
        self.gateway.answer_callback(callback_id, "Подтверждено." if changed and status == "APPROVED" else "Отклонено." if changed else "Уже обработано или недоступно.")
