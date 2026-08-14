from backend.accounts.service import AccountService
from backend.learning.models import Course, CourseModule, Lesson
from backend.learning.service import LearningPlatformService
from backend.learning_api.service import LearningPlatformAPI


def setup_course():
    learning = LearningPlatformService()
    student = learning.create_student()
    first = Lesson("l1", "Welcome", estimated_duration_minutes=5)
    second = Lesson("l2", "Practice", prerequisite_lesson_ids=["l1"], estimated_duration_minutes=10)
    third = Lesson("l3", "Review", prerequisite_lesson_ids=["l2"], estimated_duration_minutes=8)
    course = Course("course-en-a1", "English A1", "language", "A1", "English", modules=[CourseModule("m1", "Start", [first, second, third])])
    learning.create_course(course)
    learning.enroll(student.id, course.id)
    return learning, student, course


def test_path_marks_locked_current_and_completed_steps():
    learning, student, course = setup_course()
    initial = learning.learning_path_snapshot(student.id, course.id)
    assert initial.current_lesson_id == "l1"
    assert [step.unlocked for step in initial.steps] == [True, False, False]
    learning.start_lesson(student.id, course.id, "l1")
    learning.complete_lesson(student.id, course.id, "l1")
    resumed = learning.learning_path_snapshot(student.id, course.id)
    assert resumed.completion_percentage == 33.33
    assert resumed.current_lesson_id == "l2"
    assert resumed.next_lesson_id == "l2"
    assert resumed.steps[0].status.value == "completed"
    assert resumed.steps[1].unlocked is True


def test_started_lesson_is_resume_target():
    learning, student, course = setup_course()
    learning.start_lesson(student.id, course.id, "l1")
    snapshot = learning.learning_path_snapshot(student.id, course.id)
    assert snapshot.current_lesson_id == "l1"
    assert snapshot.steps[0].status.value == "in_progress"


def test_authenticated_api_exposes_serializable_learning_path():
    learning = LearningPlatformService()
    course = Course("course-de-a1", "German A1", "language", "A1", "German", modules=[CourseModule("m1", "Start", [Lesson("l1", "Hallo")])])
    learning.create_course(course)
    api = LearningPlatformAPI(AccountService(), learning)
    api.register("path@example.com", "correct horse battery staple")
    token = api.login("path@example.com", "correct horse battery staple")["session_token"]
    api.enroll(token, course.id)
    path = api.learning_path(token, course.id)
    assert path["language"] == "German"
    assert path["current_lesson_id"] == "l1"
    assert path["steps"][0]["status"] == "not_started"
