"""Application facade used equally by Telegram and future Academy clients."""

from __future__ import annotations

from backend.education.assessment import AssessmentEngine
from backend.education.conversation import ConversationEngine, ScenarioEngine
from backend.education.curriculum import CurriculumEngine
from backend.education.domain.models import (
    CEFRLevel, ConversationMode, CorrectionMode, GoalType, LearningGoal,
    LearningPlan, SkillScores, StudentProfile,
)
from backend.education.guardian import EducationGuardian
from backend.education.lessons import LessonEngine
from backend.education.review import ReviewScheduler
from backend.education.students import InMemoryStudentRepository
from backend.education.voice import VoiceLessonService


class EducationAPI:
    def __init__(self, repository: InMemoryStudentRepository | None = None, voice: VoiceLessonService | None = None):
        self.repository = repository or InMemoryStudentRepository()
        self.curriculum = CurriculumEngine()
        self.assessment = AssessmentEngine()
        self.lessons = LessonEngine()
        self.conversation = ConversationEngine()
        self.scenarios = ScenarioEngine()
        self.review = ReviewScheduler()
        self.guardian = EducationGuardian()
        self.voice = voice
        self._active_lessons = {}

    def create_student(self, platform_user_id: str, native_language: str, target_language: str, goal: GoalType, *, experience: CEFRLevel = CEFRLevel.PRE_A1, lesson_duration: int = 20, interests: list[str] | None = None, speaking_confidence: float = 0) -> StudentProfile:
        profile = StudentProfile(platform_user_id, native_language, target_language, [goal], current_level=experience, estimated_cefr_level=experience, preferred_lesson_duration=lesson_duration, interests=interests or [], speaking_confidence=speaking_confidence)
        return self.repository.create(profile)

    def start_assessment(self, platform_user_id: str, student_id: str) -> dict[str, object]:
        return self.assessment.start(self.repository.get(student_id, platform_user_id))

    def complete_assessment(self, platform_user_id: str, student_id: str, scores: SkillScores, confidence: float):
        student = self.repository.get(student_id, platform_user_id)
        result = self.assessment.complete(student, scores, confidence)
        student.estimated_cefr_level = result.overall_level
        self.repository.memory(student_id, platform_user_id).assessments.append(result)
        return result

    def create_learning_plan(self, platform_user_id: str, student_id: str, target_level: CEFRLevel | None = None) -> LearningPlan:
        student = self.repository.get(student_id, platform_user_id)
        target_level = target_level or self.curriculum.next_level(student.estimated_cefr_level)
        topics = [unit.topic for unit in self.curriculum.units_for(student.target_language) if unit.level in {student.estimated_cefr_level, target_level}]
        primary = LearningGoal(f"Maintain a 15-minute everyday conversation in {student.target_language}.", "conversation_minutes", 15)
        priorities = ["listening", "speaking", "high-frequency vocabulary"] if student.target_language.casefold() in {"english", "en"} else ["pronunciation", "high-frequency vocabulary", "case usage", "listening", "conversation"]
        plan = LearningPlan(student_id, student.target_language, student.estimated_cefr_level, target_level, primary, [], 12, 4, student.preferred_lesson_duration, priorities, topics, "adaptive active recall", "lightweight monthly assessment")
        self.repository.memory(student_id, platform_user_id).goals.append(primary)
        return plan

    def start_lesson(self, platform_user_id: str, student_id: str, duration: int | None = None):
        student = self.repository.get(student_id, platform_user_id)
        memory = self.repository.memory(student_id, platform_user_id)
        completed = {str(entry["topic"]) for entry in memory.lesson_history}
        unit = self.curriculum.select_unit(student, completed)
        difficulty = .2 + list(CEFRLevel).index(student.estimated_cefr_level) * .12
        plan = self.lessons.create(student, unit, memory, duration=duration, difficulty=difficulty)
        self._active_lessons[plan.lesson_id] = (platform_user_id, plan)
        return plan

    def submit_answer(self, platform_user_id: str, student_id: str, lesson_id: str, answer: str) -> dict[str, object]:
        self.repository.get(student_id, platform_user_id)
        owner, plan = self._active_lessons[lesson_id]
        if owner != platform_user_id or plan.student_id != student_id:
            raise PermissionError("lesson access denied")
        return {"attempt_recorded": True, "next": "analysis", "answer": answer}

    def continue_lesson(self, platform_user_id: str, student_id: str, lesson_id: str, answer: str):
        return self.submit_answer(platform_user_id, student_id, lesson_id, answer)

    def request_hint(self, platform_user_id: str, student_id: str, answer: str, level: int) -> str:
        self.repository.get(student_id, platform_user_id)
        return self.conversation.hint(answer, level)

    def finish_lesson(self, platform_user_id: str, student_id: str, lesson_id: str, *, speaking_minutes: int, performance: float):
        self.repository.get(student_id, platform_user_id)
        owner, plan = self._active_lessons.pop(lesson_id)
        if owner != platform_user_id or plan.student_id != student_id:
            raise PermissionError("lesson access denied")
        return self.lessons.finish(plan, self.repository.memory(student_id, platform_user_id), speaking_minutes=speaking_minutes, performance=performance)

    def start_conversation(self, platform_user_id: str, student_id: str, topic: str, mode: ConversationMode = ConversationMode.TUTOR_MODE, correction_mode: CorrectionMode = CorrectionMode.STANDARD):
        student = self.repository.get(student_id, platform_user_id)
        return self.conversation.start(student_id, student.estimated_cefr_level, topic, mode, correction_mode)

    async def submit_voice(self, platform_user_id: str, student_id: str, audio: bytes):
        student = self.repository.get(student_id, platform_user_id)
        if not self.voice:
            raise RuntimeError("voice learning is not configured")
        return await self.voice.submit(audio, student.target_language)

    def get_progress(self, platform_user_id: str, student_id: str):
        return self.repository.memory(student_id, platform_user_id).progress

    def get_review(self, platform_user_id: str, student_id: str):
        return self.review.due(self.repository.memory(student_id, platform_user_id).vocabulary)
