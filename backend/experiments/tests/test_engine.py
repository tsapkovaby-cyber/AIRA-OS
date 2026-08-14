from dataclasses import replace

import pytest

from backend.experiments.engine import ExperimentEngine, ExperimentError
from backend.experiments.executors import MockOutcome, MockTestExecutor
from backend.experiments.models import (
    ConfidenceLabel, Cost, Environment, EvidenceType, Experiment, ExperimentType,
    Metric, Protocol, RiskLevel, Status, TestCase as DomainTestCase,
    TestResult as DomainTestResult,
)


def make_experiment(*, repeats=3, cost=None, risk=RiskLevel.LOW, tool="Tool X"):
    case = DomainTestCase("Stable response", "Measure output", {"prompt": "same"}, "valid response",
                    "success ratio", ["mock"], 0, repeats)
    metric = Metric("quality", "Output quality", "score", "objective", raw_value=8)
    metric.normalize(0, 10)
    return Experiment(
        "Tool test", "Controlled mock test", tool, "Vendor", "LLM",
        ExperimentType.AI_TOOL_REVIEW, "founder", "aira",
        Environment("test", "2026-08-10", "1.0", settings={"temperature": 0}),
        Protocol("Does it work?", "It succeeds >= 80%", [{"prompt": "same"}], {}, repeats, []),
        [case], [metric], risk=risk, cost=cost or Cost(), tool_permissions=["mock"])


def complete(engine, experiment, outcome=MockOutcome.SUCCESS):
    engine.create_experiment(experiment)
    if experiment.status is Status.WAITING_APPROVAL:
        engine.approve_experiment(experiment.id, "founder")
    engine.start_experiment(experiment.id, MockTestExecutor(outcome))
    engine.link_evidence(experiment.id, experiment.test_cases[0].id, EvidenceType.TEXT_OUTPUT,
                         "asset://raw/1", "mock", b"unaltered")
    engine.evaluate_experiment(experiment.id)
    if experiment.status is Status.REVIEW:
        engine.guardian_review(experiment.id, True, "guardian")
    return experiment


def test_creation_protocol_validation_and_cost_approval():
    engine = ExperimentEngine(cost_threshold=5)
    experiment = make_experiment(cost=Cost(api=6))
    engine.create_experiment(experiment)
    assert experiment.cost.estimated_total == 6
    assert experiment.status is Status.WAITING_APPROVAL
    with pytest.raises(ExperimentError):
        engine.start_experiment(experiment.id, MockTestExecutor())
    engine.approve_experiment(experiment.id, "founder")
    assert experiment.approved_by == "founder"


def test_test_case_and_protocol_validation():
    experiment = make_experiment(repeats=2)
    experiment.protocol.sample_size = 1
    with pytest.raises(ValueError, match="sample size"):
        ExperimentEngine().create_experiment(experiment)
    experiment = make_experiment()
    experiment.test_cases[0].repeat_count = 0
    with pytest.raises(ValueError):
        ExperimentEngine().create_experiment(experiment)


def test_versioning_preserves_hypothesis_history():
    engine = ExperimentEngine()
    experiment = engine.create_experiment(make_experiment())
    original = experiment.history[0].snapshot["protocol"]["hypothesis"]
    protocol = replace(experiment.protocol, hypothesis="Revised before execution")
    engine.update_protocol(experiment.id, protocol, "founder")
    assert experiment.version == 2 and experiment.protocol.version == 2
    assert original == "It succeeds >= 80%"
    engine.start_experiment(experiment.id, MockTestExecutor())
    with pytest.raises(ExperimentError):
        engine.update_protocol(experiment.id, protocol, "founder")


def test_manual_result_validation_and_evidence_integrity():
    engine = ExperimentEngine()
    experiment = engine.create_experiment(make_experiment())
    case = experiment.test_cases[0]
    result = DomainTestResult("SUCCESS", "manual", {"latency": 1.2}, ["asset://file"],
                        "operator note", {"quality": 8}, attempts=3)
    engine.record_result(experiment.id, case.id, result)
    evidence = engine.link_evidence(experiment.id, case.id, EvidenceType.HUMAN_RATING,
                                    "asset://rating", "founder", b"rating=8")
    assert engine.verify_evidence(evidence, b"rating=8")
    assert not engine.verify_evidence(evidence, b"rating=9")
    with pytest.raises(ExperimentError):
        engine.record_result(experiment.id, case.id, replace(result, human_ratings={"quality": 11}))


@pytest.mark.parametrize("outcome,expected", [
    (MockOutcome.SUCCESS, Status.REVIEW), (MockOutcome.FAILED, Status.FAILED),
    (MockOutcome.TIMEOUT, Status.FAILED), (MockOutcome.PARTIAL, Status.REVIEW),
    (MockOutcome.INCONCLUSIVE, Status.INCONCLUSIVE), (MockOutcome.HIGH_COST, Status.FAILED),
    (MockOutcome.INVALID_OUTPUT, Status.FAILED),
])
def test_all_mock_outcomes_are_retained(outcome, expected):
    engine = ExperimentEngine()
    experiment = engine.create_experiment(make_experiment())
    engine.start_experiment(experiment.id, MockTestExecutor(outcome))
    engine.evaluate_experiment(experiment.id)
    assert experiment.status is expected
    assert experiment.test_cases[0].result is not None


def test_permission_denial_is_audited():
    engine = ExperimentEngine()
    experiment = make_experiment()
    experiment.tool_permissions = []
    engine.create_experiment(experiment)
    with pytest.raises(ExperimentError, match="unapproved"):
        engine.start_experiment(experiment.id, MockTestExecutor())
    assert engine.events[-1]["type"] == "ToolPermissionDenied"


def test_failure_rate_and_small_sample_confidence():
    engine = ExperimentEngine()
    experiment = complete(engine, make_experiment(repeats=1), MockOutcome.SUCCESS)
    assert experiment.confidence is ConfidenceLabel.VERY_LOW
    assert "Small sample" in experiment.limitations[0]
    assert engine.get_report(experiment.id)["sample_size"] == 1


def test_guardian_knowledge_memory_and_claim_boundary():
    engine = ExperimentEngine()
    experiment = engine.create_experiment(make_experiment())
    assert not engine.has_verified_test_claim("Tool X")
    engine.start_experiment(experiment.id, MockTestExecutor())
    engine.link_evidence(experiment.id, experiment.test_cases[0].id, EvidenceType.LOG,
                         "asset://log", "mock", b"log")
    engine.evaluate_experiment(experiment.id)
    assert not engine.has_verified_test_claim("Tool X")
    engine.guardian_review(experiment.id, True, "guardian")
    assert engine.has_verified_test_claim("Tool X")
    candidate = engine.knowledge_handoff(experiment.id)
    memory = engine.memory_handoff(experiment.id)
    assert candidate["source_experiment_id"] == experiment.id
    assert memory["related_tool"] == "Tool X"
    assert experiment.status is Status.KNOWLEDGE_UPDATED


def test_comparison_has_metric_winner_but_no_forced_overall_winner():
    engine = ExperimentEngine()
    first = complete(engine, make_experiment(tool="A"))
    second = make_experiment(tool="B")
    second.metrics[0].raw_value = 6
    second.metrics[0].normalize(0, 10)
    complete(engine, second)
    comparison = engine.compare_experiments([first.id, second.id])
    assert comparison.winner_by_metric["quality"] == first.id
    assert "no forced overall winner" in comparison.overall_result.lower()


def test_regression_event_can_preserve_historical_experiments():
    engine = ExperimentEngine()
    previous = complete(engine, make_experiment(tool="X v1"))
    current = make_experiment(tool="X v2")
    current.metrics[0].raw_value = 6.4
    current.metrics[0].normalize(0, 10)
    complete(engine, current)
    assert previous.metrics[0].raw_value == 8
    assert current.id != previous.id
    if current.metrics[0].normalized_value < previous.metrics[0].normalized_value:
        engine._event("RegressionDetected", current, previous_experiment_id=previous.id)
    assert engine.events[-1]["type"] == "RegressionDetected"
