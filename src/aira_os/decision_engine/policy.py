"""Decision Engine policy rules and classifiers."""

from __future__ import annotations

from .models import ApprovalStatus, ConfidenceBand, DecisionType, RiskLevel

FOUNDER_APPROVAL_TYPES = {
    DecisionType.PUBLISHING,
    DecisionType.STRATEGIC,
    DecisionType.BUSINESS,
    DecisionType.SECURITY,
}

CONSTITUTION_RULES = (
    "Never violate Constitution.",
    "Never execute without sufficient evidence.",
    "Never publish automatically.",
    "Never hide uncertainty.",
    "Always preserve decision history.",
    "Every important decision must be explainable.",
    "The Founder may override any decision.",
)


def confidence_band(score: float) -> ConfidenceBand:
    """Convert a percentage confidence score into the sprint-defined band."""

    if not 0 <= score <= 100:
        raise ValueError("confidence must be between 0 and 100")
    if score >= 95:
        return ConfidenceBand.VERIFIED
    if score >= 90:
        return ConfidenceBand.HIGHLY_RELIABLE
    if score >= 75:
        return ConfidenceBand.RELIABLE
    if score >= 50:
        return ConfidenceBand.NEEDS_VERIFICATION
    return ConfidenceBand.DO_NOT_RECOMMEND


def classify_risk(impact: int, reversibility: int, external_exposure: int) -> RiskLevel:
    """Classify risk from normalized 1-5 architectural scoring inputs.

    Higher impact, lower reversibility, and higher external exposure increase
    the resulting risk classification.
    """

    for value in (impact, reversibility, external_exposure):
        if value < 1 or value > 5:
            raise ValueError("risk scoring inputs must be between 1 and 5")

    score = impact + (6 - reversibility) + external_exposure
    if score >= 14:
        return RiskLevel.CRITICAL
    if score >= 11:
        return RiskLevel.HIGH
    if score >= 8:
        return RiskLevel.MEDIUM
    if score >= 5:
        return RiskLevel.LOW
    return RiskLevel.MINIMAL


def requires_approval(decision_type: DecisionType, risk: RiskLevel) -> ApprovalStatus:
    """Apply founder-control approval matrix."""

    if decision_type in FOUNDER_APPROVAL_TYPES:
        return ApprovalStatus.REQUIRED
    if risk in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
        return ApprovalStatus.REQUIRED
    return ApprovalStatus.NOT_REQUIRED


def validate_constitution(evidence_count: int, confidence: float, decision_type: DecisionType) -> list[str]:
    """Return constitution validation messages or raise for hard violations."""

    checks = list(CONSTITUTION_RULES)
    if evidence_count <= 0:
        raise ValueError("Decision violates evidence-first rule: no evidence supplied")
    if confidence < 50:
        raise ValueError("Decision confidence is below recommendation threshold")
    if decision_type is DecisionType.PUBLISHING:
        checks.append("Publishing decision marked for Founder approval; automatic publication blocked.")
    return checks
