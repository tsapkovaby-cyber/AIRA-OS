"""Curated curriculum selection and gentle adaptive sequencing."""

from __future__ import annotations

from backend.education.domain.models import CEFRLevel, CurriculumUnit, StudentProfile
from backend.education.languages.english.curriculum import ENGLISH_UNITS
from backend.education.languages.russian.curriculum import RUSSIAN_UNITS


class CurriculumEngine:
    def units_for(self, target_language: str) -> tuple[CurriculumUnit, ...]:
        language = target_language.casefold()
        if language in {"english", "en"}:
            return ENGLISH_UNITS
        if language in {"russian", "ru"}:
            return RUSSIAN_UNITS
        raise ValueError(f"unsupported target language: {target_language}")

    def select_unit(self, student: StudentProfile, completed_topics: set[str]) -> CurriculumUnit:
        units = self.units_for(student.target_language)
        same_level = [u for u in units if u.level == student.estimated_cefr_level]
        candidates = same_level or list(units)
        if candidates and all(unit.topic in completed_topics for unit in candidates):
            candidates = [unit for unit in units if unit.topic not in completed_topics] or candidates
        interest = {value.casefold() for value in student.interests}
        candidates.sort(key=lambda u: (u.topic.casefold() not in interest, u.topic in completed_topics))
        return next((unit for unit in candidates if unit.topic not in completed_topics), candidates[0])

    @staticmethod
    def adapt_difficulty(current: float, recent_performance: float) -> float:
        if recent_performance >= 0.85:
            return min(1.0, current + 0.1)
        if recent_performance <= 0.45:
            return max(0.1, current - 0.1)
        return current

    @staticmethod
    def next_level(level: CEFRLevel) -> CEFRLevel:
        levels = list(CEFRLevel)
        return levels[min(levels.index(level) + 1, len(levels) - 1)]
