"""Application controller orchestrating one natural classroom turn."""

from __future__ import annotations

from datetime import datetime, timezone

from .correction import CorrectionBuffer
from .domain import ClassroomMode, ConversationTurn, LiveClassroomSession, SessionState, Speaker
from .memory import LearningMemory
from .policy import ConversationPolicy
from .services import ConversationEngine, LanguageAnalyzer, SpeechRecognizer, SpeechSynthesizer
from .transports import ClassroomTransport


class DuplicateTurnError(ValueError):
    pass


class LiveClassroomController:
    def __init__(self, *, asr: SpeechRecognizer, analyzer: LanguageAnalyzer, engine: ConversationEngine,
                 tts: SpeechSynthesizer, transport: ClassroomTransport, memory: LearningMemory):
        self.asr, self.analyzer, self.engine = asr, analyzer, engine
        self.tts, self.transport, self.memory = tts, transport, memory
        self.sessions: dict[str, LiveClassroomSession] = {}
        self._buffers: dict[str, CorrectionBuffer] = {}
        self._policies: dict[str, ConversationPolicy] = {}
        self._idempotency: dict[str, ConversationTurn] = {}

    def start_session(self, *, student_id: str, target_language: str, support_language: str,
                      level: str, goal: str, minutes: int = 15,
                      mode: ClassroomMode = ClassroomMode.GUIDED_CONVERSATION,
                      scenario: str | None = None) -> LiveClassroomSession:
        if minutes not in {5, 10, 15, 20, 30, 45, 60}:
            raise ValueError("unsupported session duration")
        voice = "AIRA_ENGLISH_TEACHER" if target_language.lower().startswith("en") else "AIRA_RUSSIAN_TEACHER"
        session = LiveClassroomSession(student_id, target_language, support_language, level, goal,
                                       conversation_mode=mode, scenario=scenario,
                                       maximum_duration_minutes=minutes, voice_profile=voice)
        session.started_at, session.state = datetime.now(timezone.utc), SessionState.ACTIVE
        self.sessions[session.session_id] = session
        policy = ConversationPolicy(level)
        self._policies[session.session_id] = policy
        self._buffers[session.session_id] = CorrectionBuffer(policy.correction_frequency_turns)
        return session

    def receive_voice(self, session_id: str, audio: bytes, *, event_id: str,
                      audio_reference: str | None = None) -> ConversationTurn:
        if event_id in self._idempotency:
            return self._idempotency[event_id]
        session = self.sessions[session_id]
        if session.state not in {SessionState.ACTIVE, SessionState.WAITING_STUDENT}:
            raise ValueError("session is not accepting turns")
        session.state = SessionState.PROCESSING
        transcript = self.asr.transcribe(audio, session.target_language)
        turn = ConversationTurn(session_id, Speaker.STUDENT, "voice", transcript.text,
                                transcript.language, raw_audio_reference=audio_reference,
                                confidence=transcript.confidence)
        analysis = self.analyzer.analyze(transcript.text, session.target_language,
                                         session.support_language, transcript.confidence)
        turn.normalized_transcript, turn.detected_intent = analysis.normalized_text, analysis.intent
        # The reference is retained only when explicitly supplied by an approved storage layer.
        turn.raw_audio_reference = audio_reference
        turn.detected_errors = [vars_for_correction(c) for c in analysis.corrections]
        session.turns.append(turn)
        session.vocabulary.update(analysis.vocabulary)
        buffer = self._buffers[session_id]
        for correction in analysis.corrections:
            buffer.add(correction)
            session.mistakes.append(vars_for_correction(correction))
        policy = self._policies[session_id]
        if analysis.intent == "slow":
            policy.adapt(requested_speed=policy.speech_speed - 0.15)
            session.speech_speed = policy.speech_speed
        response = policy.constrain_response(self.engine.respond(session, transcript.text, analysis))
        corrections = buffer.select(len([t for t in session.turns if t.speaker == Speaker.STUDENT]))
        caption = None
        if corrections:
            item = corrections[0]
            caption = f"Correction saved: {item.original} → {item.corrected}"
            response += f" One small correction: {item.corrected}. {item.explanation}"
        turn.response_strategy = "confirm" if transcript.confidence < 0.7 else ("delayed_correction" if corrections else "continue")
        turn.response_text = response
        try:
            if session.generated_voice_turns >= session.voice_generation_limit:
                raise RuntimeError("voice generation budget reached")
            response_audio = self.tts.synthesize(response, session.target_language, session.voice_profile, policy.speech_speed)
            turn.response_audio = response_audio
            session.generated_voice_turns += 1
            self.transport.send_voice(session.student_id, response_audio, caption)
        except Exception:
            self.transport.send_text(session.student_id, response)
        session.state = SessionState.WAITING_STUDENT
        self._idempotency[event_id] = turn
        return turn

    def end_session(self, session_id: str) -> dict:
        session = self.sessions[session_id]
        session.state = SessionState.ENDING
        session.ended_at = datetime.now(timezone.utc)
        session.duration_seconds = (session.ended_at - session.started_at).total_seconds() if session.started_at else 0
        student_turns = [t for t in session.turns if t.speaker == Speaker.STUDENT]
        summary = {
            "speaking_time_seconds": session.speaking_time_seconds,
            "main_topic": session.lesson_goal,
            "new_vocabulary": sorted(session.vocabulary),
            "important_errors": session.mistakes[:3],
            "turns": len(student_turns),
            "average_utterance_words": (sum(len(t.transcript.split()) for t in student_turns) / len(student_turns)) if student_turns else 0,
            "learning_estimate_only": True,
            "recommended_review": session.lesson_goal,
            "next_lesson": session.scenario or "guided review",
        }
        session.session_summary = summary
        session.next_recommended_lesson = summary["next_lesson"]
        session.state = SessionState.COMPLETED
        self.memory.save(session.student_id, session.session_id, summary)
        return summary


def vars_for_correction(correction) -> dict:
    return {name: getattr(correction, name) for name in (
        "original", "corrected", "explanation", "category", "meaning_breaking",
        "repeated", "lesson_target", "high_frequency", "pronunciation"
    )}
