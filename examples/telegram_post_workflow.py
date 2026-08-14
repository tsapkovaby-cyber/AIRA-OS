"""Example: create and inspect the Telegram Post workflow template."""

from aira_workflow_engine import WorkflowEngine, workflow_templates

engine = WorkflowEngine()
workflow = workflow_templates()["telegram_post"]
engine.create_workflow(workflow)
engine.validate_workflow(workflow.workflow_id)
engine.approve_workflow(workflow.workflow_id, founder_approval="Founder approved architecture-only queueing.")
engine.queue_workflow(workflow.workflow_id)

print(engine.generate_report(workflow.workflow_id))
