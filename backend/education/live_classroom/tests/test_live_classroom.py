from backend.education.live_classroom.controller import LiveClassroomController
from backend.education.live_classroom.correction import Correction, CorrectionBuffer
from backend.education.live_classroom.domain import ClassroomMode, ConversationTurn, LiveClassroomSession, SessionState, Speaker
from backend.education.live_classroom.memory import InMemoryLearningMemory
from backend.education.live_classroom.policy import ConversationPolicy
from backend.education.live_classroom.services import (
    BasicConversationEngine, CanonicalVoiceTTS, LanguageAnalyzer, PassthroughASR,
    TranscriptResult, TurnDetector,
)
from backend.education.live_classroom.transports import TelegramVoiceTransport


def build_controller(asr=None, tts=None):
    transport, memory = TelegramVoiceTransport(), InMemoryLearningMemory()
    return LiveClassroomController(
        asr=asr or PassthroughASR(), analyzer=LanguageAnalyzer(),
        engine=BasicConversationEngine(), tts=tts or CanonicalVoiceTTS(),
        transport=transport, memory=memory,
    ), transport, memory


def test_session_and_turn_creation():
    session = LiveClassroomSession("s", "en", "ru", "A1", "travel")
    turn = ConversationTurn(session.session_id, Speaker.STUDENT, "voice", "hello", "en")
    assert session.state == SessionState.PLANNED
    assert turn.turn_id and turn.confidence == 1


def test_turn_detector_abstraction():
    detector = TurnDetector(700)
    assert not detector.is_complete(silence_ms=699)
    assert detector.is_complete(silence_ms=700)
    assert detector.is_complete(silence_ms=0, explicit_stop=True)


def test_correction_buffer_prioritizes_and_does_not_correct_every_turn():
    buffer = CorrectionBuffer(release_every_turns=3)
    minor = Correction("a", "b", "style", "style")
    important = Correction("go", "went", "past", "grammar", repeated=True)
    buffer.add(minor); buffer.add(important)
    assert buffer.select(1) == []
    assert buffer.select(3) == [important]
    assert len(buffer) == 1


def test_language_ratio_difficulty_and_speech_speed_adapt_safely():
    beginner, advanced = ConversationPolicy("A1"), ConversationPolicy("C1")
    assert beginner.target_language_ratio == .7
    assert advanced.target_language_ratio == 1
    beginner.adapt(struggle=True)
    assert beginner.target_language_ratio >= .7
    beginner.adapt(requested_speed=.1)
    assert beginner.speech_speed == .5


def test_low_confidence_never_creates_mistake():
    result = LanguageAnalyzer().analyze("Yesterday I go", "en", "ru", .4)
    assert result.intent == "confirm_transcript"
    assert result.corrections == []


def test_modes_produce_short_contextual_prompts():
    for mode, expected in [(ClassroomMode.PRONUNCIATION, "repeat"), (ClassroomMode.LISTENING, "train"), (ClassroomMode.ROLEPLAY, "hotel")]:
        controller, _, _ = build_controller()
        session = controller.start_session(student_id="s", target_language="en", support_language="ru", level="A1", goal="practice", mode=mode, scenario="hotel")
        turn = controller.receive_voice(session.session_id, b"hello", event_id=mode)
        assert expected in turn.response_text.lower()


def test_ru_to_en_e2e_delayed_correction_summary_and_memory():
    controller, transport, memory = build_controller()
    session = controller.start_session(student_id="ru-student", target_language="en", support_language="ru", level="A1", goal="plans")
    one = controller.receive_voice(session.session_id, b"I want go Thailand", event_id="1")
    controller.receive_voice(session.session_id, b"I like beaches", event_id="2")
    three = controller.receive_voice(session.session_id, b"I want to swim", event_id="3")
    assert one.response_strategy == "continue"
    assert "want to go" in three.response_text
    assert transport.sent[-1]["kind"] == "voice"
    summary = controller.end_session(session.session_id)
    assert summary["turns"] == 3
    assert memory.recent("ru-student")[0]["learning_estimate_only"] is True


def test_en_to_ru_e2e_and_student_memory_isolation():
    controller, _, memory = build_controller()
    session = controller.start_session(student_id="en-student", target_language="ru", support_language="en", level="A1", goal="food")
    turn = controller.receive_voice(session.session_id, "Я люблю пиццу".encode(), event_id="ru-1")
    assert "Расскажи" in turn.response_text
    controller.end_session(session.session_id)
    assert len(memory.recent("en-student")) == 1
    assert memory.recent("another-student") == []


def test_duplicate_telegram_event_is_idempotent():
    controller, transport, _ = build_controller()
    session = controller.start_session(student_id="s", target_language="en", support_language="ru", level="A1", goal="travel")
    first = controller.receive_voice(session.session_id, b"hello", event_id="update-42")
    duplicate = controller.receive_voice(session.session_id, b"hello", event_id="update-42")
    assert duplicate is first
    assert len(session.turns) == len(transport.sent) == 1


def test_voice_failure_falls_back_to_text():
    class BrokenTTS:
        def synthesize(self, *args):
            raise RuntimeError("provider down")
    controller, transport, _ = build_controller(tts=BrokenTTS())
    session = controller.start_session(student_id="s", target_language="en", support_language="ru", level="A1", goal="travel")
    controller.receive_voice(session.session_id, b"hello", event_id="x")
    assert transport.sent == [{"kind": "text", "student_id": "s", "text": "That sounds interesting. What happened next?"}]


def test_uncertain_asr_confirmation_e2e():
    class UncertainASR:
        def transcribe(self, audio, language_hint):
            return TranscriptResult("Yesterday I go", language_hint, .42)
    controller, _, _ = build_controller(asr=UncertainASR())
    session = controller.start_session(student_id="s", target_language="en", support_language="ru", level="A1", goal="past")
    turn = controller.receive_voice(session.session_id, b"noise", event_id="uncertain")
    assert turn.detected_errors == []
    assert turn.response_strategy == "confirm"
    assert session.mistakes == []


def test_canonical_voice_rejects_personality_replacement():
    try:
        CanonicalVoiceTTS().synthesize("hi", "en", "OTHER_PERSONA", 1)
    except ValueError as error:
        assert "non-canonical" in str(error)
    else:
        raise AssertionError("non-canonical voice accepted")
