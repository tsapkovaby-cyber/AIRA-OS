"""Provider ports and safe local MVP implementations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .correction import Correction
from .domain import ClassroomMode, LiveClassroomSession


@dataclass(slots=True)
class TranscriptResult:
    text: str
    language: str
    confidence: float


@dataclass(slots=True)
class AnalysisResult:
    normalized_text: str
    intent: str = "conversation"
    vocabulary: set[str] = field(default_factory=set)
    corrections: list[Correction] = field(default_factory=list)
    support_language_switch: bool = False
    complexity: int = 1


class SpeechRecognizer(Protocol):
    def transcribe(self, audio: bytes, language_hint: str) -> TranscriptResult: ...


class SpeechSynthesizer(Protocol):
    def synthesize(self, text: str, language: str, voice_profile: str, speed: float) -> bytes: ...


class ConversationEngine(Protocol):
    def respond(self, session: LiveClassroomSession, text: str, analysis: AnalysisResult) -> str: ...


class LanguageAnalyzer:
    """Rule-light analyzer adapter; production deployments inject an NLP provider."""

    def analyze(self, text: str, target_language: str, support_language: str, confidence: float) -> AnalysisResult:
        normalized = " ".join(text.strip().split())
        result = AnalysisResult(normalized_text=normalized)
        lowered = normalized.casefold()
        if confidence < 0.7:
            result.intent = "confirm_transcript"
            return result  # Never infer errors from uncertain ASR.
        if any(command in lowered for command in ("slower", "медленнее")):
            result.intent = "slow"
        elif lowered in {"repeat", "повтори"}:
            result.intent = "repeat"
        elif lowered in {"explain", "объясни"}:
            result.intent = "explain"
        elif "want go" in lowered:
            result.corrections.append(Correction("want go", "want to go", "After ‘want’, use ‘to + verb’.", "grammar", lesson_target=True))
        elif "yesterday i go" in lowered:
            result.corrections.append(Correction("Yesterday I go", "Yesterday I went", "Use the past form for a completed past event.", "grammar", high_frequency=True))
        words = [word.strip(".,!?—:;\"'").casefold() for word in normalized.split()]
        result.vocabulary = {word for word in words if len(word) > 4}
        result.support_language_switch = target_language.lower().startswith("en") and any("а" <= ch <= "я" for ch in lowered)
        result.complexity = min(5, max(1, len(words) // 6 + 1))
        return result


class BasicConversationEngine:
    def respond(self, session: LiveClassroomSession, text: str, analysis: AnalysisResult) -> str:
        if analysis.intent == "confirm_transcript":
            return f"Did you say: “{text}”? Please repeat if that is not right."
        if analysis.intent == "slow":
            return "Of course. I’ll speak more slowly. What would you like to talk about?"
        if analysis.intent == "repeat":
            previous = next((t.response_text for t in reversed(session.turns) if t.response_text), None)
            return previous or "Let’s continue. Tell me one more thing."
        if session.conversation_mode == ClassroomMode.PRONUNCIATION:
            return "Listen and repeat: think. Keep your tongue gently between your teeth."
        if session.conversation_mode == ClassroomMode.LISTENING:
            return "Listen: The train leaves at half past six. What time does it leave?"
        if session.conversation_mode == ClassroomMode.ROLEPLAY:
            return f"Welcome to the {session.scenario or 'cafe'}. How can I help you today?"
        if session.target_language.lower().startswith("ru"):
            return "Понятно. Расскажи, пожалуйста, об этом немного подробнее."
        return "That sounds interesting. What happened next?"


class PassthroughASR:
    """Deterministic test/MVP adapter accepting UTF-8 audio payloads."""

    def transcribe(self, audio: bytes, language_hint: str) -> TranscriptResult:
        return TranscriptResult(audio.decode("utf-8"), language_hint, 0.95)


class CanonicalVoiceTTS:
    allowed_profiles = {"AIRA_VOICE_IDENTITY_V1", "AIRA_ENGLISH_TEACHER", "AIRA_RUSSIAN_TEACHER"}

    def synthesize(self, text: str, language: str, voice_profile: str, speed: float) -> bytes:
        if voice_profile not in self.allowed_profiles:
            raise ValueError("non-canonical AIRA voice profile")
        return f"{voice_profile}|{language}|{speed:.2f}|{text}".encode()


@dataclass(slots=True)
class TurnDetector:
    silence_threshold_ms: int = 700

    def is_complete(self, *, silence_ms: int, explicit_stop: bool = False, provider_endpoint: bool = False) -> bool:
        return explicit_stop or provider_endpoint or silence_ms >= self.silence_threshold_ms
