"""Placement and level-assessment primitives for AIRA Academy."""
from __future__ import annotations
from dataclasses import dataclass, field

CEFR_LEVELS = ("A1", "A2", "B1", "B2", "C1", "C2")

@dataclass(slots=True)
class PlacementQuestion:
    id: str
    skill: str
    level: str
    prompt: str
    answer: str

@dataclass(slots=True)
class PlacementAnswer:
    question_id: str
    answer: str

@dataclass(slots=True)
class PlacementResult:
    student_id: str
    target_language: str
    level_system: str
    level: str
    score: float
    skill_scores: dict[str, float] = field(default_factory=dict)
    recommended_course_level: str | None = None

class PlacementAssessment:
    """Deterministic MVP placement scorer, replaceable by richer adaptive testing later."""
    def __init__(self, questions: list[PlacementQuestion], *, level_system: str = "CEFR") -> None:
        self.questions = questions
        self.level_system = level_system
        self._by_id = {question.id: question for question in questions}

    def evaluate(self, student_id: str, target_language: str, answers: list[PlacementAnswer]) -> PlacementResult:
        if not self.questions:
            raise ValueError("placement assessment requires questions")
        answered = {item.question_id: item.answer.strip().casefold() for item in answers}
        correct = 0
        skill_totals: dict[str, int] = {}
        skill_correct: dict[str, int] = {}
        highest_index = 0
        for question in self.questions:
            skill_totals[question.skill] = skill_totals.get(question.skill, 0) + 1
            is_correct = answered.get(question.id) == question.answer.strip().casefold()
            if is_correct:
                correct += 1
                skill_correct[question.skill] = skill_correct.get(question.skill, 0) + 1
                if question.level in CEFR_LEVELS:
                    highest_index = max(highest_index, CEFR_LEVELS.index(question.level))
        score = correct / len(self.questions)
        level = self._level_from_score(score, highest_index)
        skill_scores = {skill: skill_correct.get(skill, 0) / total for skill, total in skill_totals.items()}
        return PlacementResult(student_id, target_language, self.level_system, level, round(score, 4), skill_scores, level)

    @staticmethod
    def _level_from_score(score: float, highest_index: int) -> str:
        if score < .2: return "A1"
        if score < .35: return "A2"
        if score < .55: return "B1"
        if score < .72: return "B2"
        if score < .88: return "C1"
        return "C2" if highest_index >= 4 else "C1"


def reference_cefr_placement() -> PlacementAssessment:
    questions = [
        PlacementQuestion("q1", "vocabulary", "A1", "Choose the greeting: Hello / Yesterday", "Hello"),
        PlacementQuestion("q2", "grammar", "A2", "Complete: She ___ coffee every morning. drink / drinks", "drinks"),
        PlacementQuestion("q3", "reading", "B1", "Meaning of 'although': contrast / cause", "contrast"),
        PlacementQuestion("q4", "grammar", "B2", "Complete: If I ___ known, I would have called. had / have", "had"),
        PlacementQuestion("q5", "vocabulary", "C1", "Closest to 'meticulous': careful / careless", "careful"),
        PlacementQuestion("q6", "reading", "C2", "Closest to 'ubiquitous': widespread / rare", "widespread"),
    ]
    return PlacementAssessment(questions)
