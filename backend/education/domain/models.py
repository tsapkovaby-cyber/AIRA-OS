"""Typed educational records with no dependency on Telegram or AIRA Core memory."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CEFRLevel(str, Enum):
    PRE_A1 = "Pre-A1"
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class GoalType(str, Enum):
    TRAVEL = "TRAVEL"
    FRIENDS = "FRIENDS"
    RELATIONSHIPS = "RELATIONSHIPS"
    WORK = "WORK"
    RELOCATION = "RELOCATION"
    EVERYDAY_LIFE = "EVERYDAY_LIFE"
    STUDY = "STUDY"
    EXAMS = "EXAMS"
    MEDIA = "MEDIA"
    GENERAL_FLUENCY = "GENERAL_FLUENCY"
    CUSTOM = "CUSTOM"


class SafetyMode(str, Enum):
    ADULT_MODE = "ADULT_MODE"
    MINOR_MODE = "MINOR_MODE"


class CorrectionMode(str, Enum):
    SOFT = "SOFT"
    STANDARD = "STANDARD"
    INTENSIVE = "INTENSIVE"


class ConversationMode(str, Enum):
    CASUAL_FRIEND_MODE = "CASUAL_FRIEND_MODE"
    TUTOR_MODE = "TUTOR_MODE"
    IMMERSION_MODE = "IMMERSION_MODE"
    TANDEM_MODE = "TANDEM_MODE"


class MistakeCategory(str, Enum):
    GRAMMAR = "GRAMMAR"
    VOCABULARY = "VOCABULARY"
    WORD_ORDER = "WORD_ORDER"
    PRONUNCIATION = "PRONUNCIATION"
    REGISTER = "REGISTER"
    COLLOCATION = "COLLOCATION"
    PREPOSITION = "PREPOSITION"
    ARTICLE = "ARTICLE"
    TENSE = "TENSE"
    CASE = "CASE"
    GENDER = "GENDER"
    STRESS = "STRESS"
    COMPREHENSION = "COMPREHENSION"


class VocabularyStatus(str, Enum):
    NEW = "NEW"
    LEARNING = "LEARNING"
    WEAK = "WEAK"
    FAMILIAR = "FAMILIAR"
    MASTERED = "MASTERED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class EducationEvent(str, Enum):
    STUDENT_CREATED = "StudentCreated"
    ASSESSMENT_STARTED = "AssessmentStarted"
    ASSESSMENT_COMPLETED = "AssessmentCompleted"
    LESSON_STARTED = "LessonStarted"
    LESSON_COMPLETED = "LessonCompleted"
    MISTAKE_DETECTED = "MistakeDetected"
    VOCABULARY_ADDED = "VocabularyAdded"
    VOCABULARY_REVIEWED = "VocabularyReviewed"
    SKILL_IMPROVED = "SkillImproved"
    REVIEW_SCHEDULED = "ReviewScheduled"
    GOAL_REACHED = "GoalReached"


@dataclass
class SkillScores:
    speaking: float = 0
    listening: float = 0
    reading: float = 0
    writing: float = 0
    vocabulary: float = 0
    grammar: float = 0
    pronunciation: float = 0


@dataclass
class EducationCostMetrics:
    llm_cost: float = 0
    speech_recognition_cost: float = 0
    speech_synthesis_cost: float = 0
    pronunciation_analysis_cost: float = 0
    lesson_count: int = 0
    learning_hours: float = 0
    active_students: int = 0

    def ratios(self) -> dict[str, float]:
        total = self.llm_cost + self.speech_recognition_cost + self.speech_synthesis_cost + self.pronunciation_analysis_cost
        return {
            "COST_PER_LESSON": total / self.lesson_count if self.lesson_count else 0,
            "COST_PER_LEARNING_HOUR": total / self.learning_hours if self.learning_hours else 0,
            "COST_PER_ACTIVE_STUDENT": total / self.active_students if self.active_students else 0,
        }


@dataclass
class StudentProfile:
    platform_user_id: str
    native_language: str
    target_language: str
    goals: list[GoalType]
    student_id: str = field(default_factory=lambda: str(uuid4()))
    current_level: CEFRLevel = CEFRLevel.PRE_A1
    estimated_cefr_level: CEFRLevel = CEFRLevel.PRE_A1
    interests: list[str] = field(default_factory=list)
    preferred_lesson_duration: int = 20
    preferred_learning_style: str = "conversational"
    speaking_confidence: float = 0.0
    vocabulary_estimate: int = 0
    grammar_profile: dict[str, float] = field(default_factory=dict)
    pronunciation_profile: dict[str, float] = field(default_factory=dict)
    weak_areas: list[str] = field(default_factory=list)
    strong_areas: list[str] = field(default_factory=list)
    learning_schedule: dict[str, object] = field(default_factory=dict)
    progress: SkillScores = field(default_factory=SkillScores)
    safety_mode: SafetyMode = SafetyMode.ADULT_MODE
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if self.native_language.casefold() == self.target_language.casefold():
            raise ValueError("native and target languages must differ")
        if self.preferred_lesson_duration not in {5, 15, 20, 30, 45, 60}:
            raise ValueError("lesson duration must be 5, 15, 20, 30, 45, or 60")
        if not 0 <= self.speaking_confidence <= 1:
            raise ValueError("speaking confidence must be between 0 and 1")


@dataclass
class LearningGoal:
    description: str
    metric: str
    target: float


@dataclass
class LanguageAssessment:
    student_id: str
    overall_level: CEFRLevel
    skills: SkillScores
    confidence: float
    observed_strengths: list[str]
    observed_weaknesses: list[str]
    recommended_starting_point: str
    assessment_confidence: float
    disclaimer: str = "AIRA's CEFR-like result is a learning estimate, not a certification."


@dataclass
class LearningPlan:
    student_id: str
    target_language: str
    current_level: CEFRLevel
    target_level: CEFRLevel
    primary_goal: LearningGoal
    secondary_goals: list[LearningGoal]
    duration_weeks: int
    weekly_frequency: int
    lesson_duration: int
    skill_priorities: list[str]
    topic_sequence: list[str]
    review_strategy: str
    assessment_schedule: str


@dataclass(frozen=True)
class CurriculumUnit:
    level: CEFRLevel
    topic: str
    objectives: tuple[str, ...]
    vocabulary: tuple[str, ...]
    grammar: tuple[str, ...]
    listening: tuple[str, ...]
    speaking: tuple[str, ...]
    pronunciation: tuple[str, ...]
    review: tuple[str, ...] = ()


@dataclass
class LessonPlan:
    student_id: str
    level: CEFRLevel
    topic: str
    objectives: list[str]
    target_vocabulary: list[str]
    target_grammar: list[str]
    speaking_tasks: list[str]
    listening_tasks: list[str]
    pronunciation_tasks: list[str]
    review_items: list[str]
    estimated_duration: int
    difficulty: float
    lesson_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class LanguageMistake:
    student_id: str
    original_phrase: str
    corrected_phrase: str
    category: MistakeCategory
    explanation: str
    severity: int
    repeated_count: int = 1
    first_seen: datetime = field(default_factory=utcnow)
    last_seen: datetime = field(default_factory=utcnow)
    mastery_status: str = "LEARNING"


@dataclass
class VocabularyItem:
    student_id: str
    word: str
    meaning: str
    context: str
    example: str
    level: CEFRLevel
    first_seen: datetime = field(default_factory=utcnow)
    last_reviewed: datetime | None = None
    recall_strength: float = 0
    next_review: datetime = field(default_factory=utcnow)
    mistake_count: int = 0
    status: VocabularyStatus = VocabularyStatus.NEW


@dataclass
class ConversationPracticeSession:
    student_id: str
    mode: ConversationMode
    correction_mode: CorrectionMode
    topic: str
    target_language_ratio: float
    turns: list[dict[str, str]] = field(default_factory=list)
    pending_corrections: list[LanguageMistake] = field(default_factory=list)
    session_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class ProgressDashboard:
    lessons_completed: int = 0
    learning_minutes: int = 0
    speaking_minutes: int = 0
    vocabulary_learned: int = 0
    vocabulary_retained: int = 0
    recurring_mistakes: int = 0
    skills: SkillScores = field(default_factory=SkillScores)
    estimated_level: CEFRLevel = CEFRLevel.PRE_A1
    streak: int = 0


@dataclass
class LearningMemory:
    student_id: str
    goals: list[LearningGoal] = field(default_factory=list)
    progress: ProgressDashboard = field(default_factory=ProgressDashboard)
    mistakes: list[LanguageMistake] = field(default_factory=list)
    vocabulary: list[VocabularyItem] = field(default_factory=list)
    lesson_history: list[dict[str, object]] = field(default_factory=list)
    assessments: list[LanguageAssessment] = field(default_factory=list)
    preferences: dict[str, object] = field(default_factory=dict)
