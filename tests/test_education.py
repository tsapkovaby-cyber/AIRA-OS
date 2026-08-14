import asyncio
from datetime import timedelta

import pytest

from backend.education import EducationAPI
from backend.education.conversation import ConversationEngine
from backend.education.curriculum import CurriculumEngine
from backend.education.domain.models import (
    CEFRLevel, CorrectionMode, GoalType, LanguageMistake, MistakeCategory,
    SafetyMode, SkillScores, VocabularyItem, VocabularyStatus, utcnow,
)
from backend.education.grammar import GrammarEngine
from backend.education.guardian import EducationGuardian
from backend.education.review import ReviewScheduler
from backend.education.students import StudentAccessDenied
from backend.education.telegram import TelegramEducationAdapter
from backend.education.voice import Transcript, VoiceLessonService
from backend.integrations.telegram.conversation import AIRAConversationService, InMemoryConversationStore
from backend.integrations.telegram.config import TelegramConfig
from backend.integrations.telegram.gateway import IncomingMessage, TelegramGateway


class FakeProvider:
    async def generate_response(self, messages):
        return "ok"


def telegram_config():
    return TelegramConfig("token", "key", 42, "model", None, "polling", None, None, 8080)


def make_student(api, user="a", native="Russian", target="English", level=CEFRLevel.A1):
    return api.create_student(user, native, target, GoalType.GENERAL_FLUENCY, experience=level, interests=["Technology"])


def test_profile_validation_and_student_memory_isolation():
    api = EducationAPI()
    a = make_student(api)
    b = make_student(api, "b", "English", "Russian")
    api.repository.memory(a.student_id, "a").preferences["private"] = "secret"
    with pytest.raises(StudentAccessDenied):
        api.repository.memory(a.student_id, "b")
    with pytest.raises(StudentAccessDenied):
        api.repository.get(b.student_id, "a")
    with pytest.raises(ValueError):
        api.create_student("c", "English", "English", GoalType.TRAVEL)


def test_adaptive_assessment_creates_plan_without_certification_claim():
    api = EducationAPI()
    student = make_student(api)
    assert api.start_assessment("a", student.student_id)["adaptive"]
    result = api.complete_assessment("a", student.student_id, SkillScores(.75, .65, .5, .4, .6, .45, .7), .8)
    assert result.overall_level is CEFRLevel.B1
    assert "not a certification" in result.disclaimer
    plan = api.create_learning_plan("a", student.student_id)
    assert plan.primary_goal.target == 15
    assert plan.skill_priorities[:2] == ["listening", "speaking"]


def test_curriculum_selection_and_adaptation():
    api = EducationAPI()
    student = make_student(api, level=CEFRLevel.B1)
    unit = api.curriculum.select_unit(student, set())
    assert unit.topic == "Technology"
    engine = CurriculumEngine()
    assert engine.adapt_difficulty(.5, .9) == pytest.approx(.6)
    assert engine.adapt_difficulty(.5, .2) == pytest.approx(.4)


def test_micro_lesson_hint_progress_and_memory_to_next_lesson():
    api = EducationAPI()
    student = make_student(api)
    lesson = api.start_lesson("a", student.student_id, 5)
    assert lesson.estimated_duration == 5
    assert any("Active recall" in task for task in lesson.speaking_tasks)
    assert api.request_hint("a", student.student_id, "I would like coffee", 1).startswith("Think")
    assert api.request_hint("a", student.student_id, "I would like coffee", 4) == "I would like coffee"
    api.submit_answer("a", student.student_id, lesson.lesson_id, "I want coffee")
    report = api.finish_lesson("a", student.student_id, lesson.lesson_id, speaking_minutes=2, performance=.8)
    assert report["duration"] == 5
    assert api.get_progress("a", student.student_id).lessons_completed == 1
    assert api.start_lesson("a", student.student_id).topic != lesson.topic


def test_soft_correction_avoids_overcorrection():
    engine = ConversationEngine()
    session = engine.start("s", CEFRLevel.A1, "friends", correction_mode=CorrectionMode.SOFT)
    for severity in range(1, 6):
        session.pending_corrections.append(LanguageMistake("s", "bad", "better", MistakeCategory.GRAMMAR, "actionable", severity))
    assert len(engine.feedback(session)) == 2
    assert engine.feedback(session)[0].severity == 5


def test_vocabulary_review_scheduler_increases_review_after_regression():
    item = VocabularyItem("s", "agree", "соглашаться", "opinion", "I agree.", CEFRLevel.A1, recall_strength=.7)
    scheduler = ReviewScheduler()
    first = scheduler.record_recall(item, .2).next_review
    second = scheduler.record_recall(item, .2).next_review
    assert item.mistake_count == 2 and item.status is VocabularyStatus.WEAK
    assert second <= first
    item.next_review = utcnow() - timedelta(seconds=1)
    assert scheduler.due([item]) == [item]


def test_grammar_uncertainty_and_guardian():
    grammar = GrammarEngine()
    assert grammar.teach_in_context("English", "Past Simple")["prompt"].startswith("What did")
    assert grammar.teach_in_context("English", "invented rule")["status"] == "uncertain"
    guardian = EducationGuardian()
    assert not guardian.check("Keep this secret", SafetyMode.MINOR_MODE).allowed
    assert not guardian.check("solve it", SafetyMode.ADULT_MODE, homework_answer_request=True).allowed


class Recognizer:
    def __init__(self, confidence): self.confidence = confidence
    async def transcribe(self, audio, language): return Transcript("I am agree", self.confidence)


def test_low_confidence_transcription_never_records_false_mistake():
    result = asyncio.run(VoiceLessonService(Recognizer(.4)).submit(b"voice", "English"))
    assert not result["accepted"] and result["request_repeat"]
    assert "won't record a mistake" in result["message"]


def test_ru_en_and_en_ru_pilot_e2e():
    for user, native, target in (("pilot-a", "Russian", "English"), ("pilot-b", "English", "Russian")):
        api = EducationAPI(voice=VoiceLessonService(Recognizer(.95)))
        student = make_student(api, user, native, target)
        api.complete_assessment(user, student.student_id, SkillScores(.3, .3, .3, .3, .3, .3, .3), .8)
        plan = api.create_learning_plan(user, student.student_id)
        lesson = api.start_lesson(user, student.student_id)
        voice = asyncio.run(api.submit_voice(user, student.student_id, b"voice"))
        api.finish_lesson(user, student.student_id, lesson.lesson_id, speaking_minutes=6, performance=.9)
        assert plan.target_language == target and voice["accepted"]
        assert api.get_progress(user, student.student_id).speaking_minutes == 6


def test_telegram_calls_education_api_and_delete_covers_learning_memory():
    api = EducationAPI()
    adapter = TelegramEducationAdapter(api)
    conversation = AIRAConversationService(FakeProvider(), InMemoryConversationStore())
    gateway = TelegramGateway(telegram_config(), conversation, adapter)
    response = asyncio.run(gateway.handle(IncomingMessage(1, 42, 10, "/learn")))
    assert "native language" in response
    student = adapter.onboard("42", "Russian", "English", GoalType.TRAVEL)
    response = asyncio.run(gateway.handle(IncomingMessage(2, 42, 10, "/learn")))
    assert "AIRA Academy" in response
    asyncio.run(gateway.handle(IncomingMessage(3, 42, 10, "/delete_my_data")))
    assert api.repository.find_by_platform_user("42") is None
