from backend.education.domain.models import CEFRLevel, LanguageAssessment, SkillScores, StudentProfile


class AssessmentEngine:
    STAGES = ("introduction", "basic_questions", "comprehension", "short_response", "vocabulary", "grammar", "optional_voice")

    def start(self, student: StudentProfile) -> dict[str, object]:
        support = "Расскажи немного о себе." if student.native_language.casefold() in {"russian", "ru"} else "Tell me a little about yourself."
        return {"stage": self.STAGES[0], "prompt": support, "adaptive": True}

    def complete(self, student: StudentProfile, scores: SkillScores, confidence: float) -> LanguageAssessment:
        average = sum(vars(scores).values()) / 7
        thresholds = ((.15, CEFRLevel.PRE_A1), (.3, CEFRLevel.A1), (.5, CEFRLevel.A2), (.7, CEFRLevel.B1), (.85, CEFRLevel.B2), (.95, CEFRLevel.C1), (1.01, CEFRLevel.C2))
        level = next(level for threshold, level in thresholds if average < threshold)
        strengths = [name for name, value in vars(scores).items() if value >= average + .1]
        weaknesses = [name for name, value in vars(scores).items() if value <= average - .1]
        return LanguageAssessment(student.student_id, level, scores, scores.speaking, strengths, weaknesses, weaknesses[0] if weaknesses else "balanced conversation", confidence)
