"""Workflow & Execution Engine architecture for AIRA OS Sprint 008."""

from .engine import WorkflowEngine as _WorkflowEngine
from .models import (
    ApprovalGate,
    BackoffStrategy,
    ConstitutionCheck,
    ExecutionHistoryEntry,
    ExecutionPolicy,
    ExecutionState,
    Incident,
    RetryPolicy,
    Stage,
    StageStatus,
    Workflow,
    WorkflowMetrics,
    WorkflowStatus,
    WorkflowType,
)
from .templates import workflow_templates


class WorkflowEngine(_WorkflowEngine):
    """Integrated workflow facade with an explicit Founder approval boundary."""

    @staticmethod
    def _require_founder(actor: str) -> None:
        if actor != "founder":
            raise PermissionError("Only the Founder may approve or resume a gated workflow")

    def approve_workflow(self, workflow_id: str, founder_approval: str, actor: str = "founder") -> Workflow:
        self._require_founder(actor)
        return super().approve_workflow(workflow_id, founder_approval)

    def resume_workflow(self, workflow_id: str, approval: str, actor: str = "founder") -> Workflow:
        self._require_founder(actor)
        return super().resume_workflow(workflow_id, approval)


__all__ = [
    "ApprovalGate",
    "BackoffStrategy",
    "ConstitutionCheck",
    "ExecutionHistoryEntry",
    "ExecutionPolicy",
    "ExecutionState",
    "Incident",
    "RetryPolicy",
    "Stage",
    "StageStatus",
    "Workflow",
    "WorkflowEngine",
    "WorkflowMetrics",
    "WorkflowStatus",
    "WorkflowType",
    "workflow_templates",
]
