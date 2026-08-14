import pytest

from backend.learning.models import ExerciseResult, LearningProfile
from backend.learning.seeds import conversational_english_a1
from backend.learning.service import DuplicateEnrollment, LearningError, LearningPlatformService, NotFound, PrerequisiteNotMet


def setup_platform():
    service = LearningPlatformService()
    student = service.create_student()
    course = service.create_course(conversational_english_a1())
    enrollment = service.enroll(student.id, course.id)
    return service, student, course, enrollment


def test_profile_course_enrollment_and_duplicate_guard():
    service, student, course, _ = setup_platform()
    profile = service.update_profile(LearningProfile(student.id, native_language="Russian", target_languages=["English"], current_level="A1", target_level="B1"))
    assert profile.student_id == student.id
    with pytest.raises(DuplicateEnrollment):
        service.enroll(student.id, course.id)


def test_lesson_prerequisites_progress_and_recommendation():
    service, student, course, _ = setup_platform()
    first, second = course.ordered_lessons()
    assert service.next_lesson(student.id, course.id).id == first.id
    with pytest.raises(PrerequisiteNotMet):
        service.start_lesson(student.id, course.id, second.id)
    service.start_lesson(student.id, course.id, first.id)
    service.complete_lesson(student.id, course.id, first.id)
    assert service.next_lesson(student.id, course.id).id == second.id
    assert service.progress(student.id, course.id).completion_percentage == 50.0


def test_exercise_results_derive_strengths_and_weaknesses():
    service, student, course, _ = setup_platform()
    first = course.ordered_lessons()[0]
    service.submit_exercise_result(ExerciseResult(student.id, course.id, first.id, first.exercises[0].id, .9, "greetings"))
    assert service.progress(student.id, course.id).strengths == ["greetings"]
    service.submit_exercise_result(ExerciseResult(student.id, course.id, first.id, first.exercises[0].id, .2, "introductions"))
    assert service.progress(student.id, course.id).weaknesses == ["introductions"]


def test_invalid_completion_and_score_are_rejected():
    service, student, course, _ = setup_platform()
    first = course.ordered_lessons()[0]
    with pytest.raises(LearningError):
        service.complete_lesson(student.id, course.id, first.id)
    with pytest.raises(LearningError):
        service.submit_exercise_result(ExerciseResult(student.id, course.id, first.id, first.exercises[0].id, 2.0))


def test_student_isolation_and_tutor_memory_boundaries():
    service, student, course, _ = setup_platform()
    other = service.create_student()
    with pytest.raises(NotFound):
        service.progress(other.id, course.id)
    session = service.start_tutor_session(student.id, mode="text", lesson_id=course.ordered_lessons()[0].id)
    assert session.student_id == student.id
    service.memory.remember(student.id, "mistakes", "hello/hi")
    assert service.memory.recall(other.id, "mistakes") == []


def test_reference_course_is_subject_generic_platform_data():
    course = conversational_english_a1()
    assert course.subject == "language"
    assert course.language == "English"
    assert len(course.modules) == 1
    assert len(course.ordered_lessons()) == 2
