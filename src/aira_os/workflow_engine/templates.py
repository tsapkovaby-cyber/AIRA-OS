"""Workflow templates for architecture planning."""

from .models import ApprovalGate, ExecutionPolicy, Stage, Workflow, WorkflowType


def workflow_templates(owner: str = "founder") -> dict[str, Workflow]:
    """Return canonical Sprint 008 workflow templates."""
    return {
        "telegram_post": Workflow(
            goal="Publish a transparent Telegram post",
            description="Research, validate, draft, review, approve, publish, analyze, and update memory.",
            owner=owner,
            workflow_type=WorkflowType.PUBLISHING,
            execution_policy=ExecutionPolicy.SEQUENTIAL,
            approval_gates=[ApprovalGate.BEFORE_PUBLICATION, ApprovalGate.BEFORE_EXTERNAL_ACTIONS],
            stages=[
                Stage("Research", "Gather evidence for the topic.", "research-agent"),
                Stage("Knowledge Validation", "Verify evidence and sources.", "knowledge-agent"),
                Stage("Draft Creation", "Create draft content.", "content-agent"),
                Stage("Guardian Review", "Check Constitution alignment.", "guardian-engine"),
                Stage("Founder Approval", "Request explicit founder approval.", "founder"),
                Stage("Publishing", "Prepare controlled publication handoff.", "publishing-agent"),
                Stage("Analytics", "Record expected analytics hooks.", "analytics-agent"),
                Stage("Memory Update", "Store lessons and history.", "memory-agent"),
            ],
        ),
        "ai_tool_review": Workflow(
            goal="Review an AI tool",
            description="Research, test, update knowledge, compare, draft, review, approve, publish, and learn.",
            owner=owner,
            workflow_type=WorkflowType.RESEARCH,
            approval_gates=[ApprovalGate.BEFORE_PUBLICATION],
            stages=[
                Stage("Research", "Collect tool information.", "research-agent"),
                Stage("Testing", "Define test findings without external automation.", "testing-agent"),
                Stage("Knowledge Update", "Update knowledge architecture.", "knowledge-agent"),
                Stage("Comparison", "Compare with alternatives.", "analysis-agent"),
                Stage("Draft", "Create review draft.", "content-agent"),
                Stage("Guardian", "Validate safety, risk, and evidence.", "guardian-engine"),
                Stage("Founder", "Collect founder approval.", "founder"),
                Stage("Publishing", "Prepare publication handoff.", "publishing-agent"),
                Stage("Learning", "Capture lessons learned.", "learning-agent"),
            ],
        ),
        "new_ai_news": Workflow(
            goal="Process new AI news",
            description="Discover, verify, decide, plan, create content, approve publication, analyze, and learn.",
            owner=owner,
            workflow_type=WorkflowType.MONITORING,
            execution_policy=ExecutionPolicy.HYBRID,
            approval_gates=[ApprovalGate.BEFORE_PUBLICATION, ApprovalGate.BEFORE_BUSINESS_DECISIONS],
            stages=[
                Stage("Discovery", "Identify candidate news.", "monitoring-agent"),
                Stage("Verification", "Verify facts and evidence.", "research-agent"),
                Stage("Knowledge", "Map knowledge implications.", "knowledge-agent"),
                Stage("Decision", "Decide whether action is warranted.", "decision-engine"),
                Stage("Planning", "Create execution plan.", "planner-engine"),
                Stage("Content", "Prepare content draft.", "content-agent"),
                Stage("Approval", "Collect founder approval.", "founder"),
                Stage("Publication", "Prepare publication handoff.", "publishing-agent"),
                Stage("Analytics", "Track results.", "analytics-agent"),
            ],
        ),
    }
