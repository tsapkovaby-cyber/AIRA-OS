"""Decision Engine orchestration API."""

from __future__ import annotations

from .models import Alternative, ApprovalStatus, Decision, DecisionStatus, DecisionType, RiskLevel
from .policy import confidence_band, requires_approval, validate_constitution
from .store import DecisionStore


class DecisionEngine:
    """Architecture-only engine for creating, evaluating, explaining, and storing decisions."""

    def __init__(self, store: DecisionStore | None = None) -> None:
        self.store = store or DecisionStore()

    def create_decision(
        self,
        *,
        decision_type: DecisionType,
        goal: str,
        context: dict,
        inputs: dict,
        alternatives: list[Alternative],
        selected_option: Alternative,
        confidence: float,
        risk: RiskLevel,
        reasoning: str,
    ) -> Decision:
        if selected_option not in alternatives:
            raise ValueError("selected option must be present in alternatives")
        checks = validate_constitution(
            evidence_count=len(inputs.get("evidence", [])),
            confidence=confidence,
            decision_type=decision_type,
        )
        approval = requires_approval(decision_type, risk)
        status = DecisionStatus.WAITING_FOR_APPROVAL if approval is ApprovalStatus.REQUIRED else DecisionStatus.DRAFT
        decision = Decision(
            type=decision_type,
            goal=goal,
            context=context,
            inputs=inputs,
            alternatives=alternatives,
            selected_option=selected_option,
            confidence=confidence,
            risk=risk,
            reasoning=reasoning,
            constitution_checks=checks,
            required_approval=approval,
            execution_status=status,
        )
        decision.record("create", "system", "Decision created and constitution checks completed.")
        return self.store.save(decision)

    def evaluate_decision(self, decision: Decision) -> dict[str, str]:
        return {
            "confidence_band": confidence_band(decision.confidence).value,
            "risk": decision.risk.value,
            "approval": decision.required_approval.value,
            "status": decision.execution_status.value,
        }

    def explain_decision(self, decision: Decision) -> str:
        return (
            f"Why: {decision.reasoning}\n"
            f"Based on: {decision.inputs}\n"
            f"Evidence count: {len(decision.inputs.get('evidence', []))}\n"
            f"Confidence: {decision.confidence}% ({confidence_band(decision.confidence).value})\n"
            f"Alternatives considered: {', '.join(option.name for option in decision.alternatives)}\n"
            f"Selected option: {decision.selected_option.name}\n"
            f"Risk: {decision.risk.value}\n"
            f"Approval: {decision.required_approval.value}"
        )

    @staticmethod
    def _require_founder(actor: str) -> None:
        if actor != "founder":
            raise PermissionError("Only the Founder may approve or reject a decision")

    def approve_decision(self, decision_id: str, actor: str = "founder") -> Decision:
        self._require_founder(actor)
        decision = self.store.load(decision_id)
        decision.required_approval = ApprovalStatus.APPROVED
        decision.execution_status = DecisionStatus.APPROVED
        decision.record("approve", actor, "Founder approval granted.")
        return self.store.save(decision)

    def reject_decision(self, decision_id: str, actor: str = "founder") -> Decision:
        self._require_founder(actor)
        decision = self.store.load(decision_id)
        decision.required_approval = ApprovalStatus.REJECTED
        decision.execution_status = DecisionStatus.REJECTED
        decision.record("reject", actor, "Founder rejected the decision.")
        return self.store.save(decision)

    def cancel_decision(self, decision_id: str, actor: str = "system") -> Decision:
        decision = self.store.load(decision_id)
        decision.execution_status = DecisionStatus.CANCELLED
        decision.record("cancel", actor, "Decision cancelled before execution.")
        return self.store.save(decision)

    def load_decision(self, decision_id: str) -> Decision:
        return self.store.load(decision_id)

    def search_decisions(self, query: str) -> list[Decision]:
        return self.store.search(query)
