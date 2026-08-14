import pytest

from aira_os.decision_engine import Alternative, DecisionEngine, DecisionStatus, DecisionType, RiskLevel
from aira_os.decision_engine.policy import ApprovalStatus, ConfidenceBand, classify_risk, confidence_band


def option(name="Option A", risk=RiskLevel.LOW, confidence=82):
    return Alternative(
        name=name,
        pros=["auditable"],
        cons=["requires review"],
        cost="low",
        complexity="low",
        expected_result="documented recommendation",
        risk=risk,
        confidence=confidence,
        recommendation="recommended",
    )


def test_decision_engine_initializes():
    assert DecisionEngine().store is not None


def test_confidence_calculation_bands():
    assert confidence_band(97) is ConfidenceBand.VERIFIED
    assert confidence_band(92) is ConfidenceBand.HIGHLY_RELIABLE
    assert confidence_band(80) is ConfidenceBand.RELIABLE
    assert confidence_band(60) is ConfidenceBand.NEEDS_VERIFICATION
    assert confidence_band(40) is ConfidenceBand.DO_NOT_RECOMMEND


@pytest.mark.parametrize(
    ("impact", "reversibility", "exposure", "expected"),
    [
        (1, 5, 1, RiskLevel.MINIMAL),
        (2, 4, 2, RiskLevel.LOW),
        (3, 3, 3, RiskLevel.MEDIUM),
        (4, 2, 4, RiskLevel.HIGH),
        (5, 1, 5, RiskLevel.CRITICAL),
    ],
)
def test_risk_classification(impact, reversibility, exposure, expected):
    assert classify_risk(impact, reversibility, exposure) is expected


def test_approval_workflow_for_publishing():
    engine = DecisionEngine()
    selected = option("Publish Draft", RiskLevel.LOW, 96)
    decision = engine.create_decision(
        decision_type=DecisionType.PUBLISHING,
        goal="prepare publication candidate",
        context={"platform": "blog"},
        inputs={"evidence": ["editorial checklist"]},
        alternatives=[selected, option("Wait", RiskLevel.MINIMAL, 90)],
        selected_option=selected,
        confidence=96,
        risk=RiskLevel.LOW,
        reasoning="The candidate is ready for Founder review, not automatic publication.",
    )

    assert decision.required_approval is ApprovalStatus.REQUIRED
    assert decision.execution_status is DecisionStatus.WAITING_FOR_APPROVAL

    approved = engine.approve_decision(decision.id)
    assert approved.required_approval is ApprovalStatus.APPROVED
    assert approved.execution_status is DecisionStatus.APPROVED


def test_non_founder_cannot_approve_or_reject():
    engine = DecisionEngine()
    selected = option("Publish Draft", RiskLevel.LOW, 96)
    decision = engine.create_decision(
        decision_type=DecisionType.PUBLISHING,
        goal="prepare publication candidate",
        context={},
        inputs={"evidence": ["editorial checklist"]},
        alternatives=[selected],
        selected_option=selected,
        confidence=96,
        risk=RiskLevel.LOW,
        reasoning="Founder review is required.",
    )
    with pytest.raises(PermissionError, match="Founder"):
        engine.approve_decision(decision.id, actor="agent")
    with pytest.raises(PermissionError, match="Founder"):
        engine.reject_decision(decision.id, actor="agent")


def test_alternative_generation_requirement_validates_selected_option():
    engine = DecisionEngine()
    selected = option("Selected")

    with pytest.raises(ValueError, match="selected option"):
        engine.create_decision(
            decision_type=DecisionType.OPERATIONAL,
            goal="choose an option",
            context={},
            inputs={"evidence": ["ticket"]},
            alternatives=[option("Different")],
            selected_option=selected,
            confidence=80,
            risk=RiskLevel.LOW,
            reasoning="Selected option must be evaluated as an alternative.",
        )


def test_history_preservation_and_explanation():
    engine = DecisionEngine()
    selected = option("Maintain")
    decision = engine.create_decision(
        decision_type=DecisionType.MAINTENANCE,
        goal="perform internal cleanup",
        context={"system_state": "stable"},
        inputs={"evidence": ["passing tests", "low impact"]},
        alternatives=[selected, option("Wait", RiskLevel.MINIMAL, 75)],
        selected_option=selected,
        confidence=82,
        risk=RiskLevel.LOW,
        reasoning="Cleanup is low risk and supported by available evidence.",
    )

    engine.cancel_decision(decision.id)
    reloaded = engine.load_decision(decision.id)
    explanation = engine.explain_decision(reloaded)

    assert [event.action for event in reloaded.history] == ["create", "cancel"]
    assert "Evidence count: 2" in explanation
    assert "Alternatives considered: Maintain, Wait" in explanation


def test_constitution_validation_rejects_missing_evidence():
    engine = DecisionEngine()
    selected = option("Unsupported")

    with pytest.raises(ValueError, match="no evidence"):
        engine.create_decision(
            decision_type=DecisionType.OPERATIONAL,
            goal="unsupported decision",
            context={},
            inputs={"evidence": []},
            alternatives=[selected],
            selected_option=selected,
            confidence=75,
            risk=RiskLevel.LOW,
            reasoning="This should fail evidence-first validation.",
        )
