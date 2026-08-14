"""Application facade and deterministic progress engine."""
from __future__ import annotations

from .models import Course, CourseProgress, Enrollment, ExerciseResult, LearningProfile, LearningStatus, Student, new_id
from .ports import FakeTutor, InMemoryLearningMemory, LearningMemoryPort, TutorPort


class LearningError(ValueError): pass
class NotFound(LearningError): pass
class DuplicateEnrollment(LearningError): pass
class PrerequisiteNotMet(LearningError): pass


class LearningPlatformService:
    def __init__(self, *, tutor: TutorPort | None = None, memory: LearningMemoryPort | None = None) -> None:
        self.students: dict[str, Student] = {}
        self.profiles: dict[str, LearningProfile] = {}
        self.courses: dict[str, Course] = {}
        self.enrollments: dict[tuple[str, str], Enrollment] = {}
        self.results: list[ExerciseResult] = []
        self.tutor = tutor or FakeTutor()
        self.memory = memory or InMemoryLearningMemory()

    def create_student(self) -> Student:
        student = Student()
        self.students[student.id] = student
        return student

    def update_profile(self, profile: LearningProfile) -> LearningProfile:
        self._student(profile.student_id)
        self.profiles[profile.student_id] = profile
        return profile

    def create_course(self, course: Course) -> Course:
        self.courses[course.id] = course
        return course

    def enroll(self, student_id: str, course_id: str) -> Enrollment:
        self._student(student_id); self._course(course_id)
        key = (student_id, course_id)
        if key in self.enrollments:
            raise DuplicateEnrollment("student already enrolled")
        enrollment = Enrollment(id=new_id(), student_id=student_id, course_id=course_id)
        self.enrollments[key] = enrollment
        return enrollment

    def start_lesson(self, student_id: str, course_id: str, lesson_id: str) -> Enrollment:
        enrollment, course = self._context(student_id, course_id)
        lesson = self._lesson(course, lesson_id)
        if not set(lesson.prerequisite_lesson_ids).issubset(enrollment.completed_lesson_ids):
            raise PrerequisiteNotMet(lesson_id)
        enrollment.started_lesson_ids.add(lesson_id)
        enrollment.status = LearningStatus.IN_PROGRESS
        return enrollment

    def complete_lesson(self, student_id: str, course_id: str, lesson_id: str) -> Enrollment:
        enrollment, course = self._context(student_id, course_id)
        self._lesson(course, lesson_id)
        if lesson_id not in enrollment.started_lesson_ids:
            raise LearningError("lesson must be started before completion")
        enrollment.completed_lesson_ids.add(lesson_id)
        if len(enrollment.completed_lesson_ids) == len(course.ordered_lessons()):
            enrollment.status = LearningStatus.COMPLETED
        self.memory.remember(student_id, "completed_lessons", lesson_id)
        return enrollment

    def submit_exercise_result(self, result: ExerciseResult) -> ExerciseResult:
        enrollment, course = self._context(result.student_id, result.course_id)
        lesson = self._lesson(course, result.lesson_id)
        if not any(e.id == result.exercise_id for e in lesson.exercises):
            raise NotFound(result.exercise_id)
        if not 0 <= result.score <= 1:
            raise LearningError("score must be between 0 and 1")
        self.results.append(result)
        return result

    def progress(self, student_id: str, course_id: str) -> CourseProgress:
        enrollment, course = self._context(student_id, course_id)
        lessons = course.ordered_lessons()
        scores: dict[str, list[float]] = {}
        for result in self.results:
            if result.student_id == student_id and result.course_id == course_id and result.topic:
                scores.setdefault(result.topic, []).append(result.score)
        averages = {topic: sum(values)/len(values) for topic, values in scores.items()}
        return CourseProgress(
            course_id=course_id,
            completed_lessons=len(enrollment.completed_lesson_ids),
            total_lessons=len(lessons),
            completion_percentage=round((len(enrollment.completed_lesson_ids) / len(lessons) * 100) if lessons else 0, 2),
            strengths=sorted(k for k, v in averages.items() if v >= .8),
            weaknesses=sorted(k for k, v in averages.items() if v < .6),
        )

    def next_lesson(self, student_id: str, course_id: str):
        enrollment, course = self._context(student_id, course_id)
        for lesson in course.ordered_lessons():
            if lesson.id not in enrollment.completed_lesson_ids and set(lesson.prerequisite_lesson_ids).issubset(enrollment.completed_lesson_ids):
                return lesson
        return None

    def start_tutor_session(self, student_id: str, *, mode: str, lesson_id: str | None = None):
        return self.tutor.start_session(self._student(student_id), mode=mode, lesson_id=lesson_id)

    def _student(self, student_id: str) -> Student:
        try: return self.students[student_id]
        except KeyError: raise NotFound(student_id) from None

    def _course(self, course_id: str) -> Course:
        try: return self.courses[course_id]
        except KeyError: raise NotFound(course_id) from None

    def _context(self, student_id: str, course_id: str):
        self._student(student_id); course = self._course(course_id)
        try: return self.enrollments[(student_id, course_id)], course
        except KeyError: raise NotFound("enrollment") from None

    @staticmethod
    def _lesson(course: Course, lesson_id: str):
        for lesson in course.ordered_lessons():
            if lesson.id == lesson_id: return lesson
        raise NotFound(lesson_id)
