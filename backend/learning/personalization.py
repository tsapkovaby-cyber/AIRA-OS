"""Deterministic learning-memory and personalization engine for AIRA Academy."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, field
from .models import ExerciseResult, LearningProfile
from .ports import LearningMemoryPort

@dataclass(slots=True)
class LearningInsight:
    student_id: str
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    repeated_topics: list[str] = field(default_factory=list)
    recommended_focus: list[str] = field(default_factory=list)
    confidence: str = "building"

class PersonalizationEngine:
    """Builds explainable recommendations without requiring a paid AI call."""
    def __init__(self, memory: LearningMemoryPort) -> None:
        self.memory = memory

    def record_result(self, result: ExerciseResult) -> None:
        if not result.topic:
            return
        category = "strength_topics" if result.score >= .8 else "weak_topics" if result.score < .6 else "practice_topics"
        self.memory.remember(result.student_id, category, result.topic)

    def record_conversation_issue(self, student_id: str, topic: str) -> None:
        topic = topic.strip()
        if topic:
            self.memory.remember(student_id, "conversation_issues", topic)

    def insight(self, student_id: str, profile: LearningProfile | None = None) -> LearningInsight:
        strengths = self._rank(self.memory.recall(student_id, "strength_topics"))
        weak = self.memory.recall(student_id, "weak_topics") + self.memory.recall(student_id, "conversation_issues")
        weaknesses = self._rank(weak)
        practice = self._rank(self.memory.recall(student_id, "practice_topics"))
        counts = Counter(weak)
        repeated = [topic for topic, count in counts.most_common() if count >= 2]
        focus = self._unique(repeated + weaknesses + practice)
        if profile:
            profile.strengths = strengths[:5]
            profile.weaknesses = weaknesses[:5]
        confidence = "growing" if len(strengths) >= len(weaknesses) and strengths else "building"
        return LearningInsight(student_id, strengths[:5], weaknesses[:5], repeated[:5], focus[:5], confidence)

    @staticmethod
    def _rank(items: list[str]) -> list[str]:
        counts = Counter(items)
        return [item for item, _ in counts.most_common()]

    @staticmethod
    def _unique(items: list[str]) -> list[str]:
        return list(dict.fromkeys(items))
