import pytest

from aira_workflow_engine import (
    ApprovalGate,
    ConstitutionCheck,
    ExecutionPolicy,
    RetryPolicy,
    Stage,
    StageStatus,
    Workflow,
    WorkflowEngine,
    WorkflowStatus,
    WorkflowType,
    workflow_templates,
)


def sample_workflow() -> Workflow:
    first = Stage("Plan", "Plan execution.", "planner-engine")
    second = Stage("Review", "Review execution.", "guardian-engine", dependencies=[first.stage_id])
    return Workflow(
        goal="Test workflow",
        description="Validate engine architecture.",
        owner="founder",
        stages=[first, second],
        workflow_type=WorkflowType.DEVELOPMENT,
        execution_policy=ExecutionPolicy.SEQUENTIAL,
        approval_gates=[ApprovalGate.BEFORE_ARCHITECTURE_CHANGES],
    )


def test_workflow_creation_records_history():
    engine = WorkflowEngine()
    workflow = engine.create_workflow(sample_workflow())

    assert workflow.workflow_id in engine.workflows
    assert workflow.status == WorkflowStatus.DRAFT
    assert workflow.execution_history[-1].action == "create"


def test_stage_and_dependency_validation():
    workflow = sample_workflow()
    workflow.validate()

    broken = Workflow(
        goal="Broken",
        description="Broken dependencies.",
        owner="founder",
        stages=[Stage("Broken", "Missing dependency.", "agent", dependencies=["missing-stage"])],
        workflow_type=WorkflowType.DEVELOPMENT,
    )

    with pytest.raises(ValueError, match="Unknown stage dependencies"):
        broken.validate()


def test_retry_logic_retries_recoverable_failure():
    engine = WorkflowEngine()
    stage = Stage("Retry", "Retry recoverable error.", "agent", retry_policy=RetryPolicy(maximum_attempts=2))
    workflow = Workflow("Retry goal", "Retry description", "founder", [stage], WorkflowType.MAINTENANCE)
    engine.create_workflow(workflow)

    engine.handle_failure(workflow.workflow_id, stage.stage_id, "temporary failure")

    assert stage.status == StageStatus.RETRYING
    assert stage.retry_count == 1
    assert workflow.incidents == []


def test_failure_after_retry_limit_creates_incident_and_pauses():
    engine = WorkflowEngine()
    stage = Stage("Fail", "Fail after attempts.", "agent", retry_policy=RetryPolicy(maximum_attempts=1))
    workflow = Workflow("Failure goal", "Failure description", "founder", [stage], WorkflowType.MAINTENANCE)
    engine.create_workflow(workflow)

    engine.handle_failure(workflow.workflow_id, stage.stage_id, "permanent failure")

    assert stage.status == StageStatus.FAILED
    assert workflow.status == WorkflowStatus.PAUSED
    assert len(workflow.incidents) == 1
    assert engine.alerts


def test_approval_gate_and_constitution_blocking():
    engine = WorkflowEngine(ConstitutionCheck(evidence_sufficient=False, reason="Evidence missing"))
    workflow = engine.create_workflow(sample_workflow())
    engine.validate_workflow(workflow.workflow_id)

    with pytest.raises(ValueError, match="guardian blocked"):
        engine.approve_workflow(workflow.workflow_id, founder_approval="Founder approves")

    assert workflow.status == WorkflowStatus.PAUSED
    assert workflow.execution_history[-1].agent == "guardian"


def test_missing_founder_approval_waits_for_approval():
    engine = WorkflowEngine()
    workflow = engine.create_workflow(sample_workflow())
    engine.validate_workflow(workflow.workflow_id)

    with pytest.raises(ValueError, match="founder approval required"):
        engine.approve_workflow(workflow.workflow_id, founder_approval="")

    assert workflow.status == WorkflowStatus.WAITING_APPROVAL


def test_monitoring_report_and_completion():
    engine = WorkflowEngine()
    workflow = engine.create_workflow(sample_workflow())
    engine.validate_workflow(workflow.workflow_id)
    engine.approve_workflow(workflow.workflow_id, "Founder approved")
    engine.queue_workflow(workflow.workflow_id)
    engine.start_workflow(workflow.workflow_id)

    for stage in workflow.stages:
        engine.record_stage_result(workflow.workflow_id, stage.stage_id, StageStatus.SUCCEEDED, "stage passed")

    engine.complete_workflow(workflow.workflow_id)
    report = engine.generate_report(workflow.workflow_id)
    tracking = engine.track_workflow(workflow.workflow_id)

    assert report["status"] == WorkflowStatus.COMPLETED.value
    assert tracking["progress"] == 1
    assert tracking["metrics"]["execution_success_rate"] == 1


def test_templates_include_required_sprint_workflows():
    templates = workflow_templates()

    assert set(templates) == {"telegram_post", "ai_tool_review", "new_ai_news"}
    assert ApprovalGate.BEFORE_PUBLICATION in templates["telegram_post"].approval_gates
    assert templates["new_ai_news"].execution_policy == ExecutionPolicy.HYBRID
