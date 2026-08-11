"""Classroom transport boundary and Telegram voice MVP."""

from dataclasses import dataclass, field
from typing import Protocol


class ClassroomTransport(Protocol):
    def send_voice(self, student_id: str, audio: bytes, caption: str | None = None) -> None: ...
    def send_text(self, student_id: str, text: str) -> None: ...


@dataclass
class TelegramVoiceTransport:
    sent: list[dict] = field(default_factory=list)

    def send_voice(self, student_id: str, audio: bytes, caption: str | None = None) -> None:
        self.sent.append({"kind": "voice", "student_id": student_id, "audio": audio, "caption": caption})

    def send_text(self, student_id: str, text: str) -> None:
        self.sent.append({"kind": "text", "student_id": student_id, "text": text})
