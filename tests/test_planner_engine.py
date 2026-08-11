import pytest

from aira_os.planner_engine import GoalType, PlannerEngine, PlanningLevel, PlanStatus, TaskStatus
from aira_os.planner_engine.dependencies import DependencyEngine
from aira_os.planner_engine.models import ComplexityEstimate, Priority, Task


def test_plan_creation_initializes_workflow_and_tasks():
    engine = PlannerEngine()
    goal = engine.create_goal(
        "Build Planner Engine",
        "Design the Planner Engine architecture",
        GoalType.DEVELOPMENT,
        PlanningLevel.INITIATIVE,
    )

    plan = engine.generate_plan(goal)

    assert plan.goal == goal
    assert plan.workflow.name == "Development Architecture"
    assert len(plan.tasks) == len(plan.workflow.phases)
    assert all(task.status == TaskStatus.PLANNED for task in plan.tasks)


def test_dependency_validation_detects_missing_duplicate_and_cycle():
    estimate = ComplexityEstimate(30, 2, 2, 0.8)
    first = Task("Research", "Research", Priority.HIGH, "Planner", "Research Agent", estimate)
    duplicate = Task("Research", "Duplicate", Priority.HIGH, "Planner", "Research Agent", estimate)
    missing = Task("Draft", "Draft", Priority.HIGH, "Planner", "Content Agent", estimate, dependencies={"missing"})
    first.dependencies.add(duplicate.task_id)
    duplicate.dependencies.add(first.task_id)

    issues = DependencyEngine().validate([first, duplicate, missing])

    assert {issue.code for issue in issues} == {"duplicate_task", "missing_dependency", "circular_dependency"}


def test_task_ordering_respects_dependencies():
    estimate = ComplexityEstimate(30, 2, 2, 0.8)
    research = Task("Research", "Research", Priority.HIGH, "Planner", "Research Agent", estimate)
    draft = Task("Draft", "Draft", Priority.HIGH, "Planner", "Content Agent", estimate, dependencies={research.task_id})

    ordered = DependencyEngine().order([draft, research])

    assert [task.task_id for task in ordered] == [research.task_id, draft.task_id]


def test_priority_calculation_uses_planning_level():
    engine = PlannerEngine()
    goal = engine.create_goal("Strategy", "Strategic objective", GoalType.BUSINESS, PlanningLevel.STRATEGIC_OBJECTIVE)

    plan = engine.generate_plan(goal)

    assert {task.priority for task in plan.tasks} == {Priority.CRITICAL}


def test_approval_workflow_moves_tasks_to_queue():
    engine = PlannerEngine()
    goal = engine.create_goal("Research Topic", "Produce research plan", GoalType.RESEARCH, PlanningLevel.PROJECT)
    plan = engine.generate_plan(goal)

    engine.request_approval(plan.plan_id)
    approved = engine.approve_plan(plan.plan_id)

    assert approved.status == PlanStatus.APPROVED
    assert all(task.status == TaskStatus.QUEUED for task in approved.tasks)


def test_agent_assignment_updates_task_history():
    engine = PlannerEngine()
    task = Task("Knowledge", "Update knowledge", Priority.MEDIUM, "Planner", "", ComplexityEstimate(20, 1, 1, 0.9))

    assigned = engine.assign_agent(task, "knowledge_update")

    assert assigned.agent == "Knowledge Agent"
    assert "Knowledge Agent" in assigned.history[-1]


def test_progress_tracking_counts_statuses():
    engine = PlannerEngine()
    goal = engine.create_goal("Content", "Write content", GoalType.CONTENT, PlanningLevel.PROJECT)
    plan = engine.generate_plan(goal)
    plan.tasks[0].transition(TaskStatus.COMPLETED, "Done")
    plan.tasks[1].transition(TaskStatus.BLOCKED, "Waiting on input")

    progress = engine.track_progress(plan.plan_id)

    assert progress.completed == 1
    assert progress.blocked == 1
    assert progress.forecast == "at_risk"


def test_invalid_dependency_order_raises():
    estimate = ComplexityEstimate(30, 2, 2, 0.8)
    task = Task("Draft", "Draft", Priority.HIGH, "Planner", "Content Agent", estimate, dependencies={"missing"})

    with pytest.raises(ValueError):
        DependencyEngine().order([task])
