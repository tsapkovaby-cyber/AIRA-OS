"""Student-facing learning-path projections for resumable Academy study."""
from __future__ import annotations
from dataclasses import dataclass
from .models import Course, Enrollment, LearningStatus

@dataclass(frozen=True, slots=True)
class LearningPathStep:
    lesson_id: str
    title: str
    position: int
    status: LearningStatus
    unlocked: bool
    estimated_duration_minutes: int

@dataclass(frozen=True, slots=True)
class LearningPathSnapshot:
    student_id: str
    course_id: str
    course_title: str
    language: str | None
    level: str
    completion_percentage: float
    completed_lessons: int
    total_lessons: int
    current_lesson_id: str | None
    next_lesson_id: str | None
    steps: tuple[LearningPathStep, ...]


def build_learning_path_snapshot(enrollment: Enrollment, course: Course) -> LearningPathSnapshot:
    lessons = course.ordered_lessons()
    completed = enrollment.completed_lesson_ids
    current_id: str | None = None
    next_id: str | None = None
    steps: list[LearningPathStep] = []
    for position, lesson in enumerate(lessons, start=1):
        unlocked = set(lesson.prerequisite_lesson_ids).issubset(completed)
        if lesson.id in completed:
            status = LearningStatus.COMPLETED
        elif lesson.id in enrollment.started_lesson_ids:
            status = LearningStatus.IN_PROGRESS
            if current_id is None:
                current_id = lesson.id
        else:
            status = LearningStatus.NOT_STARTED
        if next_id is None and status != LearningStatus.COMPLETED and unlocked:
            next_id = lesson.id
        steps.append(LearningPathStep(lesson.id, lesson.title, position, status, unlocked, lesson.estimated_duration_minutes))
    if current_id is None:
        current_id = next_id
    total = len(lessons)
    pct = round((len(completed) / total * 100) if total else 0, 2)
    return LearningPathSnapshot(enrollment.student_id, course.id, course.title, course.language, course.level, pct, len(completed), total, current_id, next_id, tuple(steps))
