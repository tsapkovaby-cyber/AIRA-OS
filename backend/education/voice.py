"""Provider-neutral voice lesson pipeline preserving AIRA's canonical identity."""

from dataclasses import dataclass
from typing import Protocol


AIRA_VOICE_IDENTITY = "AIRA_VOICE_IDENTITY_V1"
VOICE_PROFILES = {"english": "AIRA_ENGLISH_TEACHER", "russian": "AIRA_RUSSIAN_TEACHER"}


@dataclass(frozen=True)
class Transcript:
    text: str
    confidence: float


class SpeechRecognizer(Protocol):
    async def transcribe(self, audio: bytes, language: str) -> Transcript: ...


class SpeechSynthesizer(Protocol):
    async def synthesize(self, text: str, voice_identity: str, profile: str, speed: float) -> bytes: ...


class VoiceLessonService:
    def __init__(self, recognizer: SpeechRecognizer, synthesizer: SpeechSynthesizer | None = None):
        self.recognizer, self.synthesizer = recognizer, synthesizer

    async def submit(self, audio: bytes, language: str) -> dict[str, object]:
        transcript = await self.recognizer.transcribe(audio, language)
        if transcript.confidence < .65:
            return {"accepted": False, "request_repeat": True, "message": "I may have heard that incorrectly. Please repeat it; I won't record a mistake yet."}
        return {"accepted": True, "request_repeat": False, "transcript": transcript.text, "confidence": transcript.confidence}

    async def speak(self, text: str, language: str, speed: float = 1.0) -> bytes:
        if not self.synthesizer:
            raise RuntimeError("speech synthesis is not configured")
        profile = VOICE_PROFILES[language.casefold()]
        return await self.synthesizer.synthesize(text, AIRA_VOICE_IDENTITY, profile, max(.6, min(1.2, speed)))
