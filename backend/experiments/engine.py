"""Application service enforcing lifecycle, evidence, approval and handoff rules."""

from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
from typing import Any, Callable

from .executors import TestExecutor
from .models import (
    ApprovalStatus, Comparison, ConfidenceLabel, Evidence, EvidenceType, Experiment,
    HistoryEntry, RiskLevel, Status, TestResult, utcnow,
)


class ExperimentError(ValueError):
    pass


class ExperimentEngine:
    """In-memory reference service; repositories can replace its storage later."""

    def __init__(self, cost_threshold: float = 10.0, event_sink: Callable[[dict], None] | None = None):
        self.experiments: dict[str, Experiment] = {}
        self.cost_threshold = cost_threshold
        self.events: list[dict[str, Any]] = []
        self.event_sink = event_sink

    def _event(self, name: str, experiment: Experiment, **payload: Any) -> None:
        event = {"type": name, "experiment_id": experiment.id, "at": utcnow().isoformat(), **payload}
        self.events.append(event)
        if self.event_sink:
            self.event_sink(event)

    def _history(self, experiment: Experiment, action: str, actor: str) -> None:
        experiment.history.append(HistoryEntry(experiment.version, action, actor, utcnow(), experiment.snapshot()))

    def create_experiment(self, experiment: Experiment) -> Experiment:
        experiment.protocol.validate(experiment.test_cases, experiment.metrics)
        experiment.cost.estimated_total = experiment.cost.calculated()
        needs_approval = (experiment.cost.estimated_total > self.cost_threshold or
                          experiment.risk in {RiskLevel.HIGH, RiskLevel.CRITICAL} or
                          bool(experiment.protocol.approval_requirements))
        experiment.approval_status = ApprovalStatus.PENDING if needs_approval else ApprovalStatus.NOT_REQUIRED
        experiment.status = Status.WAITING_APPROVAL if needs_approval else Status.DESIGNED
        self._history(experiment, "created", experiment.created_by)
        self.experiments[experiment.id] = experiment
        self._event("ExperimentProposed", experiment)
        return experiment

    def update_protocol(self, experiment_id: str, protocol: Any, actor: str) -> Experiment:
        experiment = self.get(experiment_id)
        if experiment.status in {Status.RUNNING, Status.COLLECTING_RESULTS, Status.EVALUATING,
                                 Status.REVIEW, Status.COMPLETED, Status.KNOWLEDGE_UPDATED, Status.ARCHIVED}:
            raise ExperimentError("protocol cannot be changed after execution begins")
        protocol.version = experiment.protocol.version + 1
        protocol.validate(experiment.test_cases, experiment.metrics)
        experiment.version += 1
        experiment.protocol = protocol
        self._history(experiment, "protocol_updated", actor)
        return experiment

    def approve_experiment(self, experiment_id: str, founder: str) -> Experiment:
        experiment = self.get(experiment_id)
        if experiment.approval_status is not ApprovalStatus.PENDING:
            raise ExperimentError("experiment is not waiting for approval")
        experiment.approval_status = ApprovalStatus.APPROVED
        experiment.approved_by = founder
        experiment.status = Status.APPROVED
        self._history(experiment, "approved", founder)
        self._event("ExperimentApproved", experiment)
        return experiment

    def cancel_experiment(self, experiment_id: str, actor: str, reason: str) -> Experiment:
        experiment = self.get(experiment_id)
        if experiment.status in {Status.COMPLETED, Status.KNOWLEDGE_UPDATED, Status.ARCHIVED}:
            raise ExperimentError("completed experiments cannot be cancelled")
        if not reason.strip():
            raise ExperimentError("cancellation reason is required")
        experiment.status = Status.CANCELLED
        experiment.limitations.append(f"Cancelled: {reason}")
        self._history(experiment, "cancelled", actor)
        return experiment

    def start_experiment(self, experiment_id: str, executor: TestExecutor) -> Experiment:
        experiment = self.get(experiment_id)
        if experiment.approval_status is ApprovalStatus.PENDING:
            raise ExperimentError("founder approval required")
        if experiment.status not in {Status.DESIGNED, Status.APPROVED, Status.SCHEDULED}:
            raise ExperimentError("experiment cannot start from current status")
        required = {tool for case in experiment.test_cases for tool in case.required_tools}
        denied = required - set(experiment.tool_permissions)
        if denied:
            self._event("ToolPermissionDenied", experiment, tools=sorted(denied))
            raise ExperimentError(f"unapproved tools: {sorted(denied)}")
        experiment.status = Status.RUNNING
        self._event("ExperimentStarted", experiment)
        for case in sorted(experiment.test_cases, key=lambda item: item.execution_order):
            self._event("TestCaseStarted", experiment, test_case_id=case.id)
            case.result = executor.execute(case)
            case.status = case.result.status
            self._event("TestCaseCompleted", experiment, test_case_id=case.id, status=case.status)
        experiment.status = Status.COLLECTING_RESULTS
        return experiment

    def record_result(self, experiment_id: str, test_case_id: str, result: TestResult) -> None:
        experiment = self.get(experiment_id)
        case = next((c for c in experiment.test_cases if c.id == test_case_id), None)
        if case is None:
            raise ExperimentError("test case does not belong to experiment")
        if result.attempts < 1 or result.failures < 0 or result.failures > result.attempts:
            raise ExperimentError("invalid attempt counts")
        if any(not isinstance(value, (int, float)) for value in result.numeric_metrics.values()):
            raise ExperimentError("numeric metrics must be numbers")
        if any(not ref.strip() for ref in result.file_references):
            raise ExperimentError("file references cannot be blank")
        if any(value < 0 or value > 10 for value in result.human_ratings.values()):
            raise ExperimentError("human ratings must be between 0 and 10")
        case.result, case.status = result, result.status
        experiment.status = Status.COLLECTING_RESULTS

    def link_evidence(self, experiment_id: str, test_case_id: str, evidence_type: EvidenceType,
                      storage_reference: str, source: str, content: bytes | None = None,
                      checksum: str | None = None) -> Evidence:
        experiment = self.get(experiment_id)
        if not any(case.id == test_case_id for case in experiment.test_cases):
            raise ExperimentError("evidence must link to an experiment test case")
        digest = sha256(content).hexdigest() if content is not None else checksum
        if not digest or not storage_reference.strip():
            raise ExperimentError("storage reference and checksum are required")
        evidence = Evidence(evidence_type, storage_reference, digest, source, test_case_id)
        experiment.evidence.append(evidence)
        return evidence

    @staticmethod
    def verify_evidence(evidence: Evidence, content: bytes) -> bool:
        return sha256(content).hexdigest() == evidence.checksum

    def evaluate_experiment(self, experiment_id: str) -> Experiment:
        experiment = self.get(experiment_id)
        results = [case.result for case in experiment.test_cases]
        if any(result is None for result in results):
            raise ExperimentError("all test cases, including failures, must be recorded")
        experiment.status = Status.EVALUATING
        attempts = sum(result.attempts for result in results if result)
        failures = sum(result.failures for result in results if result)
        successful = attempts - failures
        ratio = successful / attempts if attempts else 0
        evidence_quality = min(1, len(experiment.evidence) / max(1, len(results)))
        score = min(1, attempts / 20) * .45 + ratio * .35 + evidence_quality * .20
        experiment.confidence = (ConfidenceLabel.VERY_LOW if score < .25 else
                                 ConfidenceLabel.LOW if score < .45 else
                                 ConfidenceLabel.MEDIUM if score < .65 else
                                 ConfidenceLabel.HIGH if score < .85 else ConfidenceLabel.VERY_HIGH)
        if attempts < 3:
            experiment.confidence = ConfidenceLabel.VERY_LOW
            experiment.limitations.append("Small sample; universal claims are not supported.")
        statuses = {result.status for result in results if result}
        if statuses <= {"FAILED", "TIMEOUT", "INVALID", "BLOCKED"}:
            experiment.status = Status.FAILED
            experiment.conclusion = "Experiment failed; failed outputs were retained."
            self._event("ExperimentFailed", experiment)
        elif "INCONCLUSIVE" in statuses or not attempts:
            experiment.status = Status.INCONCLUSIVE
            experiment.conclusion = "Results are inconclusive; further controlled testing is required."
            self._event("ExperimentInconclusive", experiment)
        else:
            experiment.status = Status.REVIEW
            experiment.conclusion = f"Observed success rate: {ratio:.1%} across {attempts} attempts."
        self._history(experiment, "evaluated", "experiment-engine")
        return experiment

    def guardian_review(self, experiment_id: str, approved: bool, reviewer: str,
                        limitations: list[str] | None = None) -> Experiment:
        experiment = self.get(experiment_id)
        if experiment.status is not Status.REVIEW:
            raise ExperimentError("only experiments in review can be verified")
        experiment.limitations.extend(limitations or [])
        experiment.status = Status.COMPLETED if approved else Status.BLOCKED
        self._history(experiment, "guardian_review", reviewer)
        self._event("ExperimentReviewed", experiment, approved=approved, reviewer=reviewer)
        if approved:
            self._event("ExperimentCompleted", experiment)
        return experiment

    def knowledge_handoff(self, experiment_id: str) -> dict[str, Any]:
        experiment = self.get(experiment_id)
        if experiment.status is not Status.COMPLETED:
            raise ExperimentError("only Guardian-verified completed experiments can create knowledge")
        candidate = {"source_experiment_id": experiment.id, "question": experiment.protocol.question,
                     "conclusion": experiment.conclusion, "confidence": experiment.confidence.value,
                     "limitations": list(experiment.limitations), "evidence_ids": [e.id for e in experiment.evidence]}
        reference = f"knowledge-candidate:{experiment.id}:v{experiment.version}"
        experiment.knowledge_references.append(reference)
        self._event("KnowledgeCandidateCreated", experiment, reference=reference)
        return candidate

    def memory_handoff(self, experiment_id: str) -> dict[str, Any]:
        experiment = self.get(experiment_id)
        if not experiment.knowledge_references:
            raise ExperimentError("knowledge handoff must precede memory handoff")
        memory = {"context": experiment.protocol.question, "action": experiment.title,
                  "outcome": experiment.conclusion, "lesson": experiment.limitations,
                  "confidence": experiment.confidence.value, "related_tool": experiment.tool,
                  "related_knowledge": list(experiment.knowledge_references)}
        experiment.memory_references.append(f"experience-memory:{experiment.id}:v{experiment.version}")
        experiment.status = Status.KNOWLEDGE_UPDATED
        return memory

    def compare_experiments(self, ids: list[str]) -> Comparison:
        experiments = [self.get(item) for item in ids]
        if len(experiments) < 2 or any(e.status not in {Status.COMPLETED, Status.KNOWLEDGE_UPDATED, Status.ARCHIVED} for e in experiments):
            raise ExperimentError("comparison requires two verified completed experiments")
        common = set(m.name for m in experiments[0].metrics)
        for experiment in experiments[1:]:
            common &= {m.name for m in experiment.metrics}
        normalized = {e.id: {m.name: m.normalized_value for m in e.metrics
                             if m.name in common and m.normalized_value is not None} for e in experiments}
        winners: dict[str, str | None] = {}
        for metric in sorted(common):
            values = [(e.id, normalized[e.id].get(metric)) for e in experiments]
            available = [(key, value) for key, value in values if value is not None]
            if not available:
                winners[metric] = None
            else:
                maximum = max(value for _, value in available)
                tied = [key for key, value in available if value == maximum]
                winners[metric] = tied[0] if len(tied) == 1 else None
        confidence = min((e.confidence for e in experiments), key=list(ConfidenceLabel).index)
        return Comparison(ids, [e.tool for e in experiments], sorted(common), normalized, winners,
                          ["A null winner means tied or unavailable data."],
                          "Results are metric-specific; no forced overall winner.", confidence,
                          [item for e in experiments for item in e.limitations])

    def get_report(self, experiment_id: str) -> dict[str, Any]:
        experiment = self.get(experiment_id)
        return {"executive_summary": experiment.conclusion, "question": experiment.protocol.question,
                "hypothesis": experiment.protocol.hypothesis, "method": asdict(experiment.protocol),
                "environment": asdict(experiment.environment), "test_cases": [asdict(c) for c in experiment.test_cases],
                "metrics": [asdict(m) for m in experiment.metrics], "evidence": [asdict(e) for e in experiment.evidence],
                "failures": [asdict(c) for c in experiment.test_cases if c.result and c.result.failures],
                "sample_size": sum(c.result.attempts for c in experiment.test_cases if c.result),
                "limitations": experiment.limitations, "confidence": experiment.confidence.value,
                "conclusion": experiment.conclusion, "recommended_next_step": "Guardian review" if experiment.status is Status.REVIEW else None}

    def search_experiments(self, **filters: Any) -> list[Experiment]:
        allowed = {"tool", "category", "status", "experiment_type", "confidence"}
        if set(filters) - allowed:
            raise ExperimentError("unsupported search filter")
        return [e for e in self.experiments.values()
                if all(getattr(e, key) == value for key, value in filters.items())]

    def has_verified_test_claim(self, tool: str) -> bool:
        return any(e.tool == tool and e.status in {Status.COMPLETED, Status.KNOWLEDGE_UPDATED, Status.ARCHIVED}
                   and bool(e.evidence) for e in self.experiments.values())

    def get(self, experiment_id: str) -> Experiment:
        try:
            return self.experiments[experiment_id]
        except KeyError as error:
            raise ExperimentError("experiment not found") from error
