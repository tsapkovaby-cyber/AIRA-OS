from dataclasses import dataclass

from backend.education.domain.models import SafetyMode


@dataclass(frozen=True)
class GuardianDecision:
    allowed: bool
    reason: str = ""


class EducationGuardian:
    MINOR_BLOCKED = {"sexual", "keep this secret", "hide from your parents"}

    def check(self, content: str, safety_mode: SafetyMode, *, homework_answer_request: bool = False, claims_verified: bool = True) -> GuardianDecision:
        lowered = content.casefold()
        if safety_mode is SafetyMode.MINOR_MODE and any(term in lowered for term in self.MINOR_BLOCKED):
            return GuardianDecision(False, "content is not appropriate for minor learning mode")
        if homework_answer_request:
            return GuardianDecision(False, "AIRA can teach, guide, and check, but should not complete assessed work")
        if not claims_verified:
            return GuardianDecision(False, "teaching claim requires an approved source")
        return GuardianDecision(True)
