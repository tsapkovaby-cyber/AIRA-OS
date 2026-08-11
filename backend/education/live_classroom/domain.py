"""Domain model for transport-independent language classroom sessions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SessionState(StrEnum):
    PLANNED = "PLANNED"
    READY = "READY"
    CONNECTING = "CONNECTING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    WAITING_STUDENT = "WAITING_STUDENT"
    PROCESSING = "PROCESSING"
    ENDING = "ENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ClassroomMode(StrEnum):
    FREE_CONVERSATION = "FREE_CONVERSATION"
    GUIDED_CONVERSATION = "GUIDED_CONVERSATION"
    ROLEPLAY = "ROLEPLAY"
    PRONUNCIATION = "PRONUNCIATION"
    LISTENING = "LISTENING"
    VOCABULARY = "VOCABULARY"
    GRAMMAR_IN_CONTEXT = "GRAMMAR_IN_CONTEXT"
    EXAM_SPEAKING = "EXAM_SPEAKING"
    TANDEM_PREP = "TANDEM_PREP"
    FLUENCY = "FLUENCY"


class CorrectionMode(StrEnum):
    DELAYED = "DELAYED"
    IMMEDIATE = "IMMEDIATE"
    INTENSIVE = "INTENSIVE"


class Speaker(StrEnum):
    STUDENT = "STUDENT"
    AIRA = "AIRA"


@dataclass(slots=True)
class ConversationTurn:
    session_id: str
    speaker: Speaker
    input_type: str
    transcript: str
    language: str
    turn_id: str = field(default_factory=lambda: str(uuid4()))
    raw_audio_reference: str | None = None
    normalized_transcript: str = ""
    confidence: float = 1.0
    detected_intent: str | None = None
    detected_errors: list[dict[str, Any]] = field(default_factory=list)
    response_strategy: str | None = None
    response_text: str | None = None
    response_audio: bytes | None = None
    created_at: datetime = field(default_factory=utcnow)


@dataclass(slots=True)
class PronunciationTarget:
    sound: str
    word: str
    phrase: str
    target_stress: str | None = None
    common_error: str | None = None
    student_attempt: str | None = None
    score: float | None = None
    feedback: str | None = None
    retry_count: int = 0
    mastery: float = 0.0


@dataclass(slots=True)
class SkillMastery:
    skill: str
    recognition_score: float = 0.0
    guided_use: float = 0.0
    independent_use: float = 0.0
    recent_accuracy: float = 0.0
    confidence: float = 0.0
    last_practiced: datetime | None = None
    next_review: datetime | None = None


@dataclass(slots=True)
class SpeakingConfidenceProfile:
    response_latency_seconds: float = 0.0
    average_utterance_words: float = 0.0
    self_corrections: int = 0
    support_language_dependence: float = 0.0
    continuation_rate: float = 0.0
    student_self_rating: str | None = None


@dataclass(slots=True)
class CostMetrics:
    asr: float = 0.0
    llm: float = 0.0
    tts: float = 0.0
    pronunciation: float = 0.0

    @property
    def total(self) -> float:
        return self.asr + self.llm + self.tts + self.pronunciation


@dataclass(slots=True)
class LiveClassroomSession:
    student_id: str
    target_language: str
    support_language: str
    current_level: str
    lesson_goal: str
    conversation_mode: ClassroomMode = ClassroomMode.GUIDED_CONVERSATION
    scenario: str | None = None
    correction_mode: CorrectionMode = CorrectionMode.DELAYED
    speech_speed: float = 1.0
    voice_profile: str = "AIRA_VOICE_IDENTITY_V1"
    session_id: str = field(default_factory=lambda: str(uuid4()))
    state: SessionState = SessionState.PLANNED
    started_at: datetime | None = None
    ended_at: datetime | None = None
    duration_seconds: float = 0.0
    speaking_time_seconds: float = 0.0
    aira_speaking_time_seconds: float = 0.0
    mistakes: list[dict[str, Any]] = field(default_factory=list)
    vocabulary: set[str] = field(default_factory=set)
    pronunciation_notes: list[str] = field(default_factory=list)
    learning_outcomes: list[str] = field(default_factory=list)
    session_summary: dict[str, Any] | None = None
    next_recommended_lesson: str | None = None
    turns: list[ConversationTurn] = field(default_factory=list)
    costs: CostMetrics = field(default_factory=CostMetrics)
    maximum_cost: float = 5.0
    maximum_duration_minutes: int = 15
    voice_generation_limit: int = 120
    generated_voice_turns: int = 0

    def transition(self, state: SessionState) -> None:
        terminal = {SessionState.COMPLETED, SessionState.FAILED, SessionState.CANCELLED}
        if self.state in terminal:
            raise ValueError("a terminal session cannot transition")
        self.state = state
