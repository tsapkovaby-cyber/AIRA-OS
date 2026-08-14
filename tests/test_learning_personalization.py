from backend.learning.models import Course, CourseModule, Exercise, ExerciseResult, LearningProfile, Lesson
from backend.learning.service import LearningPlatformService


def setup_learning():
    service = LearningPlatformService()
    student = service.create_student()
    profile = service.update_profile(LearningProfile(student.id, current_level="A1"))
    lesson = Lesson("l1", "Introductions", exercises=[Exercise("e1", "Say hello", "speaking", "introductions")])
    service.create_course(Course("c1", "English A1", "English", "A1", modules=[CourseModule("m1", "Start", [lesson])]))
    service.enroll(student.id, "c1")
    return service, student, profile


def test_results_become_personalized_strengths_and_weaknesses():
    service, student, profile = setup_learning()
    service.submit_exercise_result(ExerciseResult(student.id, "c1", "l1", "e1", .4, "articles"))
    service.submit_exercise_result(ExerciseResult(student.id, "c1", "l1", "e1", .9, "greetings"))
    insight = service.learning_insight(student.id)
    assert insight.weaknesses == ["articles"]
    assert insight.strengths == ["greetings"]
    assert profile.weaknesses == ["articles"]
    assert profile.strengths == ["greetings"]


def test_repeated_conversation_errors_are_prioritized():
    service, student, _ = setup_learning()
    service.record_conversation_issue(student.id, "past tense")
    service.record_conversation_issue(student.id, "past tense")
    service.record_conversation_issue(student.id, "word order")
    insight = service.learning_insight(student.id)
    assert insight.repeated_topics == ["past tense"]
    assert insight.recommended_focus[0] == "past tense"


def test_memory_is_isolated_per_student():
    service, first, _ = setup_learning()
    second = service.create_student()
    service.record_conversation_issue(first.id, "articles")
    assert service.learning_insight(second.id).weaknesses == []
