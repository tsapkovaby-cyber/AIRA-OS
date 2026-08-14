from backend.education.domain.models import CEFRLevel, ConversationMode, ConversationPracticeSession, CorrectionMode, LanguageMistake


class ConversationEngine:
    def start(self, student_id: str, level: CEFRLevel, topic: str, mode: ConversationMode = ConversationMode.TUTOR_MODE, correction_mode: CorrectionMode = CorrectionMode.STANDARD) -> ConversationPracticeSession:
        ratio = {CEFRLevel.PRE_A1: .5, CEFRLevel.A1: .6, CEFRLevel.A2: .75, CEFRLevel.B1: .9}.get(level, 1.0)
        if mode is ConversationMode.IMMERSION_MODE:
            ratio = 1.0
        return ConversationPracticeSession(student_id, mode, correction_mode, topic, ratio)

    def feedback(self, session: ConversationPracticeSession) -> list[LanguageMistake]:
        mistakes = sorted(session.pending_corrections, key=lambda item: (-item.severity, -item.repeated_count))
        if session.correction_mode is CorrectionMode.SOFT:
            return mistakes[:2]
        if session.correction_mode is CorrectionMode.STANDARD:
            return [m for m in mistakes if m.severity >= 2 or m.repeated_count > 1][:4]
        return mistakes

    @staticmethod
    def hint(answer: str, level: int) -> str:
        if level not in {1, 2, 3, 4}:
            raise ValueError("hint level must be 1 through 4")
        words = answer.split()
        return ({1: "Think about the situation and intended meaning.", 2: words[0], 3: " ".join(words[:max(1, len(words) // 2)]), 4: answer})[level]


class ScenarioEngine:
    ROLES = {"cafe": "barista", "hotel": "hotel receptionist", "airport": "airport employee", "work": "colleague", "neighbor": "neighbor"}

    def create(self, student_id: str, scenario: str, level: CEFRLevel) -> dict[str, str]:
        role = self.ROLES.get(scenario.casefold(), "patient conversation partner")
        return {"student_id": student_id, "scenario": scenario, "aira_role": role, "level": level.value, "instruction": f"You are in a {scenario}. Try to achieve your goal; AIRA will respond naturally as the {role}."}
