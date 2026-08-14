"""Architecture-only Workflow & Execution Engine.

This engine transforms execution plans into controlled workflow records. It does
not execute external work; it validates, queues, monitors, pauses, resumes, and
reports workflow state for future specialized agents.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime

from .models import (
    ApprovalGate,
    ConstitutionCheck,
    ExecutionHistoryEntry,
    Incident,
    Stage,
    StageStatus,
    Workflow,
    WorkflowMetrics,
    WorkflowStatus,
)


class WorkflowEngine:
    """In-memory architecture facade for Sprint 008 acceptance tests."""

    def __init__(self, constitution_check: ConstitutionCheck | None = None) -> None:
        self.constitution_check = constitution_check or ConstitutionCheck()
        self.workflows: dict[str, Workflow] = {}
        self.execution_queue: list[str] = []
        self.alerts: list[str] = []

    def create_workflow(self, workflow: Workflow) -> Workflow:
        workflow.validate()
        workflow.record(ExecutionHistoryEntry("workflow-engine", "create", "created", "execution plan received"))
        self.workflows[workflow.workflow_id] = workflow
        return workflow

    def validate_workflow(self, workflow_id: str) -> Workflow:
        workflow = self._get(workflow_id)
        workflow.validate()
        workflow.status = WorkflowStatus.VALIDATED
        workflow.record(ExecutionHistoryEntry("workflow-engine", "validate", "validated", "stage and dependency checks passed"))
        return workflow

    def approve_workflow(self, workflow_id: str, founder_approval: str) -> Workflow:
        workflow = self._get(workflow_id)
        self._enforce_constitution(workflow, founder_approval)
        workflow.status = WorkflowStatus.APPROVED
        workflow.record(ExecutionHistoryEntry("founder", "approve", "approved", "founder approval recorded", founder_approval))
        return workflow

    def queue_workflow(self, workflow_id: str) -> Workflow:
        workflow = self._get(workflow_id)
        if workflow.status not in {WorkflowStatus.APPROVED, WorkflowStatus.RESUMED}:
            raise ValueError("workflow must be approved or resumed before queueing")
        workflow.status = WorkflowStatus.QUEUED
        if workflow_id not in self.execution_queue:
            self.execution_queue.append(workflow_id)
        workflow.record(ExecutionHistoryEntry("workflow-engine", "queue", "queued", "workflow added to execution queue"))
        return workflow

    def start_workflow(self, workflow_id: str) -> Workflow:
        workflow = self._get(workflow_id)
        if workflow.status != WorkflowStatus.QUEUED:
            raise ValueError("workflow must be queued before running")
        self._enforce_constitution(workflow, "approval previously recorded")
        workflow.status = WorkflowStatus.RUNNING
        workflow.stages[0].status = StageStatus.RUNNING
        workflow.record(ExecutionHistoryEntry("workflow-engine", "start", "running", "first stage marked running"))
        return workflow

    def pause_workflow(self, workflow_id: str, reason: str) -> Workflow:
        workflow = self._get(workflow_id)
        workflow.status = WorkflowStatus.PAUSED
        workflow.record(ExecutionHistoryEntry("workflow-engine", "pause", "paused", reason))
        self.alerts.append(f"Workflow {workflow_id} paused: {reason}")
        return workflow

    def resume_workflow(self, workflow_id: str, approval: str) -> Workflow:
        workflow = self._get(workflow_id)
        if workflow.status not in {WorkflowStatus.PAUSED, WorkflowStatus.WAITING_APPROVAL}:
            raise ValueError("only paused or approval-waiting workflows can resume")
        self._enforce_constitution(workflow, approval)
        workflow.status = WorkflowStatus.RESUMED
        workflow.record(ExecutionHistoryEntry("founder", "resume", "resumed", "approval gate cleared", approval))
        return workflow

    def cancel_workflow(self, workflow_id: str, reason: str) -> Workflow:
        workflow = self._get(workflow_id)
        workflow.status = WorkflowStatus.CANCELLED
        workflow.record(ExecutionHistoryEntry("workflow-engine", "cancel", "cancelled", reason))
        return workflow

    def assign_agent(self, workflow_id: str, stage_id: str, agent: str) -> Workflow:
        workflow = self._get(workflow_id)
        if not any(stage.stage_id == stage_id for stage in workflow.stages):
            raise ValueError("stage not found")
        workflow.assigned_agents[stage_id] = agent
        workflow.record(ExecutionHistoryEntry("workflow-engine", "assign_agent", "assigned", f"{agent} assigned to {stage_id}"))
        return workflow

    def record_stage_result(self, workflow_id: str, stage_id: str, status: StageStatus, reason: str) -> Workflow:
        workflow = self._get(workflow_id)
        stage = next((item for item in workflow.stages if item.stage_id == stage_id), None)
        if stage is None:
            raise ValueError("stage not found")
        stage.status = status
        workflow.record(ExecutionHistoryEntry(stage.required_agent, "stage_result", status.value, reason))
        self._refresh_metrics(workflow)
        return workflow

    def handle_failure(self, workflow_id: str, stage_id: str, cause: str, critical: bool = False) -> Workflow:
        workflow = self._get(workflow_id)
        stage = next((item for item in workflow.stages if item.stage_id == stage_id), None)
        if stage is None:
            raise ValueError("stage not found")
        if not critical and stage.can_retry and stage.retry_policy.automatic_retry:
            stage.retry_count += 1
            stage.status = StageStatus.RETRYING
            workflow.record(ExecutionHistoryEntry("workflow-engine", "retry", "retrying", cause))
        else:
            stage.status = StageStatus.FAILED
            workflow.status = WorkflowStatus.PAUSED if not critical else WorkflowStatus.CANCELLED
            incident = Incident(workflow.workflow_id, cause, "workflow execution interrupted", stage.required_agent)
            incident.timeline.extend(workflow.execution_history[-5:])
            workflow.incidents.append(incident)
            self.alerts.append(f"Incident {incident.incident_id}: {cause}")
            workflow.record(ExecutionHistoryEntry("workflow-engine", "incident", "created", cause))
        self._refresh_metrics(workflow)
        return workflow

    def request_approval(self, workflow_id: str, gate: ApprovalGate, reason: str) -> Workflow:
        workflow = self._get(workflow_id)
        if gate not in workflow.approval_gates:
            workflow.approval_gates.append(gate)
        workflow.status = WorkflowStatus.WAITING_APPROVAL
        workflow.record(ExecutionHistoryEntry("workflow-engine", "approval_request", "waiting", reason))
        return workflow

    def complete_workflow(self, workflow_id: str) -> Workflow:
        workflow = self._get(workflow_id)
        if any(stage.status not in {StageStatus.SUCCEEDED, StageStatus.COMPLETED} for stage in workflow.stages):
            raise ValueError("all stages must succeed or complete before workflow completion")
        workflow.status = WorkflowStatus.COMPLETED
        workflow.record(ExecutionHistoryEntry("workflow-engine", "complete", "completed", "all stages completed"))
        self._refresh_metrics(workflow)
        return workflow

    def archive_workflow(self, workflow_id: str) -> Workflow:
        workflow = self._get(workflow_id)
        if workflow.status != WorkflowStatus.COMPLETED:
            raise ValueError("only completed workflows can be archived")
        workflow.status = WorkflowStatus.ARCHIVED
        workflow.record(ExecutionHistoryEntry("workflow-engine", "archive", "archived", "history retained"))
        return workflow

    def track_workflow(self, workflow_id: str) -> dict[str, object]:
        workflow = self._get(workflow_id)
        return {
            "workflow_id": workflow.workflow_id,
            "status": workflow.status.value,
            "progress": self._progress(workflow),
            "metrics": asdict(workflow.metrics),
            "incidents": len(workflow.incidents),
            "updated_date": workflow.updated_date.isoformat(),
        }

    def generate_report(self, workflow_id: str) -> dict[str, object]:
        workflow = self._get(workflow_id)
        return {
            "workflow": workflow.workflow_id,
            "goal": workflow.goal,
            "status": workflow.status.value,
            "stages": [{"id": stage.stage_id, "title": stage.title, "status": stage.status.value} for stage in workflow.stages],
            "history_count": len(workflow.execution_history),
            "metrics": asdict(workflow.metrics),
            "alerts": list(self.alerts),
        }

    def search_workflows(self, *, status: WorkflowStatus | None = None, owner: str | None = None) -> list[Workflow]:
        return [
            workflow
            for workflow in self.workflows.values()
            if (status is None or workflow.status == status) and (owner is None or workflow.owner == owner)
        ]

    def _get(self, workflow_id: str) -> Workflow:
        try:
            return self.workflows[workflow_id]
        except KeyError as exc:
            raise ValueError("workflow not found") from exc

    def _enforce_constitution(self, workflow: Workflow, approval: str | None) -> None:
        if not approval:
            workflow.status = WorkflowStatus.WAITING_APPROVAL
            raise ValueError("founder approval required")
        if not self.constitution_check.can_continue:
            workflow.status = WorkflowStatus.PAUSED
            workflow.record(ExecutionHistoryEntry("guardian", "constitution_check", "blocked", self.constitution_check.reason))
            raise ValueError(f"guardian blocked workflow: {self.constitution_check.reason}")

    def _refresh_metrics(self, workflow: Workflow) -> None:
        completed = sum(stage.status in {StageStatus.SUCCEEDED, StageStatus.COMPLETED} for stage in workflow.stages)
        failed = sum(stage.status == StageStatus.FAILED for stage in workflow.stages)
        retry_total = sum(stage.retry_count for stage in workflow.stages)
        elapsed = (datetime.now(workflow.created_date.tzinfo) - workflow.created_date).total_seconds()
        workflow.metrics = WorkflowMetrics(
            duration_seconds=elapsed,
            execution_success_rate=completed / len(workflow.stages),
            average_retry_count=retry_total / len(workflow.stages),
            failure_rate=failed / len(workflow.stages),
            incident_count=len(workflow.incidents),
            workflow_efficiency=completed / max(1, completed + failed + retry_total),
        )

    def _progress(self, workflow: Workflow) -> float:
        complete = sum(stage.status in {StageStatus.SUCCEEDED, StageStatus.COMPLETED} for stage in workflow.stages)
        return complete / len(workflow.stages)
