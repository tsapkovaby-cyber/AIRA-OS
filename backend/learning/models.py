"""Core domain models for the AIRA Learning Platform."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

def new_id()->str:return str(uuid4())
def now()->datetime:return datetime.now(timezone.utc)
class LearningStatus(str,Enum): NOT_STARTED="not_started"; IN_PROGRESS="in_progress"; COMPLETED="completed"
@dataclass(slots=True)
class Student: id:str=field(default_factory=new_id); created_at:datetime=field(default_factory=now)
@dataclass(slots=True)
class LearningGoal: id:str; description:str; target:str|None=None
@dataclass(slots=True)
class StudentPreference: key:str; value:str
@dataclass(slots=True)
class LearningProfile:
    student_id:str; native_language:str|None=None; target_languages:list[str]=field(default_factory=list); current_level:str|None=None; target_level:str|None=None; learning_goals:list[str]=field(default_factory=list); preferred_learning_style:str|None=None; daily_learning_target_minutes:int=20; interests:list[str]=field(default_factory=list); strengths:list[str]=field(default_factory=list); weaknesses:list[str]=field(default_factory=list)
@dataclass(slots=True)
class Exercise: id:str; title:str; kind:str; topic:str|None=None
@dataclass(slots=True)
class Assessment: id:str; title:str; exercise_ids:list[str]=field(default_factory=list); passing_score:float=.7
@dataclass(slots=True)
class Lesson:
    id:str; title:str; description:str=""; learning_objectives:list[str]=field(default_factory=list); content:str=""; difficulty:str="beginner"; estimated_duration_minutes:int=10; prerequisite_lesson_ids:list[str]=field(default_factory=list); exercises:list[Exercise]=field(default_factory=list)
@dataclass(slots=True)
class CourseModule: id:str; title:str; lessons:list[Lesson]=field(default_factory=list)
@dataclass(slots=True)
class Course:
    id:str; title:str; subject:str; level:str; language:str|None=None; description:str=""; modules:list[CourseModule]=field(default_factory=list)
    def ordered_lessons(self)->list[Lesson]:return [l for m in self.modules for l in m.lessons]
@dataclass(slots=True)
class LearningPath: student_id:str; course_id:str; lesson_ids:list[str]
@dataclass(slots=True)
class Enrollment:
    id:str; student_id:str; course_id:str; status:LearningStatus=LearningStatus.NOT_STARTED; completed_lesson_ids:set[str]=field(default_factory=set); started_lesson_ids:set[str]=field(default_factory=set); created_at:datetime=field(default_factory=now); last_activity_date:str|None=None; streak_days:int=0
@dataclass(slots=True)
class LessonProgress: student_id:str; course_id:str; lesson_id:str; status:LearningStatus
@dataclass(slots=True)
class ExerciseResult:
    student_id:str; course_id:str; lesson_id:str; exercise_id:str; score:float; topic:str|None=None; created_at:datetime=field(default_factory=now)
@dataclass(slots=True)
class CourseProgress:
    course_id:str; completed_lessons:int; total_lessons:int; completion_percentage:float; strengths:list[str]; weaknesses:list[str]; streak_days:int=0
@dataclass(slots=True)
class TutorSession: id:str; student_id:str; mode:str; lesson_id:str|None=None; created_at:datetime=field(default_factory=now)
