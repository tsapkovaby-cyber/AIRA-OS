"""Planner Engine orchestration API.

This module coordinates planning artifacts only. It never executes tasks,
starts workers, sends notifications, or integrates with calendars.
"""

from __future__ import annotations

from .dependencies import DependencyEngine
from .models import (
    AgentCapability,
    ComplexityEstimate,
    ExecutionPlan,
    ExecutionStrategy,
    Goal,
    GoalType,
    PlanStatus,
    PlanningLevel,
    Priority,
    ProgressReport,
    Task,
    TaskStatus,
    Workflow,
)


DEFAULT_AGENTS = (
    AgentCapability("Research Agent", ("research", "source_analysis"), 2),
    AgentCapability("Knowledge Agent", ("knowledge_update", "taxonomy"), 2),
    AgentCapability("Content Agent", ("draft", "content"), 1),
    AgentCapability("Guardian", ("review", "approval_gate", "constitution"), 1),
    AgentCapability("Publishing Agent", ("publishing", "analytics"), 1),
    AgentCapability("Development Agent", ("architecture", "implementation_plan"), 1),
)


class PlannerEngine:
    """Create and manage structured plans without executing work."""

    def __init__(self, agents: tuple[AgentCapability, ...] = DEFAULT_AGENTS) -> None:
        self.agents = {agent.name: agent for agent in agents}
        self.dependencies = DependencyEngine()
        self.plans: dict[str, ExecutionPlan] = {}

    def create_goal(
        self,
        title: str,
        objective: str,
        goal_type: GoalType,
        level: PlanningLevel,
        success_criteria: tuple[str, ...] = (),
        constraints: tuple[str, ...] = (),
    ) -> Goal:
        return Goal(title, objective, goal_type, level, success_criteria=success_criteria, constraints=constraints)

    def generate_plan(self, goal: Goal) -> ExecutionPlan:
        workflow = self._select_workflow(goal)
        tasks = self._generate_tasks(goal, workflow)
        ordered_tasks = self.dependencies.order(tasks)
        plan = ExecutionPlan(goal=goal, tasks=ordered_tasks, workflow=workflow)
        plan.dependency_issues = self.dependencies.validate(ordered_tasks)
        plan.roadmap_updates.append(f"Add {goal.title} to Sprint Progress and Backlog for approval")
        self.plans[plan.plan_id] = plan
        return plan

    def update_plan(self, plan_id: str, tasks: list[Task]) -> ExecutionPlan:
        plan = self._get_plan(plan_id)
        if plan.status == PlanStatus.APPROVED:
            raise ValueError("approved plans cannot be structurally updated")
        plan.tasks = self.dependencies.order(tasks)
        plan.dependency_issues = self.dependencies.validate(plan.tasks)
        return plan

    def approve_plan(self, plan_id: str) -> ExecutionPlan:
        plan = self._get_plan(plan_id)
        plan.approve()
        return plan

    def reject_plan(self, plan_id: str, reason: str) -> ExecutionPlan:
        plan = self._get_plan(plan_id)
        plan.reject(reason)
        return plan

    def archive_plan(self, plan_id: str) -> ExecutionPlan:
        plan = self._get_plan(plan_id)
        plan.status = PlanStatus.ARCHIVED
        return plan

    def assign_agent(self, task: Task, required_capability: str) -> Task:
        for agent in self.agents.values():
            if required_capability in agent.responsibilities:
                task.agent = agent.name
                task.history.append(f"Assigned to {agent.name} for {required_capability}")
                return task
        raise ValueError(f"No agent supports capability: {required_capability}")

    def search_plans(self, query: str) -> list[ExecutionPlan]:
        query_lower = query.lower()
        return [
            plan
            for plan in self.plans.values()
            if query_lower in plan.goal.title.lower() or query_lower in plan.goal.objective.lower()
        ]

    def track_progress(self, plan_id: str) -> ProgressReport:
        plan = self._get_plan(plan_id)
        total = len(plan.tasks)
        completed = sum(task.status == TaskStatus.COMPLETED for task in plan.tasks)
        blocked = sum(task.status == TaskStatus.BLOCKED for task in plan.tasks)
        remaining = total - completed
        risk = blocked / total if total else 0
        velocity = completed / total if total else 0
        forecast = "on_track" if blocked == 0 else "at_risk"
        return ProgressReport(plan.plan_id, completed, remaining, blocked, 0, risk, velocity, forecast)

    def generate_report(self, plan_id: str) -> str:
        progress = self.track_progress(plan_id)
        plan = self._get_plan(plan_id)
        return (
            f"Plan {plan.plan_id} for {plan.goal.title}: "
            f"{progress.completed} completed, {progress.remaining} remaining, "
            f"{progress.blocked} blocked, forecast={progress.forecast}"
        )

    def request_approval(self, plan_id: str) -> ExecutionPlan:
        plan = self._get_plan(plan_id)
        if plan.dependency_issues:
            raise ValueError("dependency issues must be resolved before approval")
        plan.status = PlanStatus.WAITING_GUARDIAN_REVIEW
        plan.request_founder_approval()
        return plan

    def _select_workflow(self, goal: Goal) -> Workflow:
        templates = {
            GoalType.CONTENT: Workflow("Telegram Post", ExecutionStrategy.SEQUENTIAL, ("Research", "Knowledge", "Draft", "Review", "Approval", "Publish", "Analytics", "Knowledge Update")),
            GoalType.RESEARCH: Workflow("Research", ExecutionStrategy.SEQUENTIAL, ("Scope", "Research", "Synthesis", "Review", "Knowledge Update")),
            GoalType.DEVELOPMENT: Workflow("Development Architecture", ExecutionStrategy.HYBRID, ("Requirements", "Architecture", "Task Graph", "Review", "Approval")),
            GoalType.MARKETING: Workflow("Campaign", ExecutionStrategy.HYBRID, ("Research", "Content", "Review", "Approval", "Publishing", "Analytics")),
        }
        return templates.get(goal.goal_type, Workflow("Generic Planning", ExecutionStrategy.HYBRID, ("Scope", "Plan", "Review", "Approval")))

    def _generate_tasks(self, goal: Goal, workflow: Workflow) -> list[Task]:
        tasks: list[Task] = []
        previous_id: str | None = None
        for index, phase in enumerate(workflow.phases, start=1):
            agent = self._agent_for_phase(phase)
            task = Task(
                title=f"{index}. {phase}: {goal.title}",
                description=f"Plan the {phase.lower()} phase for objective: {goal.objective}",
                priority=self._priority_for_goal(goal),
                owner="Planner Engine",
                agent=agent,
                estimate=ComplexityEstimate(estimated_duration_minutes=60, difficulty=min(goal.level.value + 1, 5), risk=2, confidence=0.7),
                status=TaskStatus.PLANNED,
                dependencies={previous_id} if previous_id and workflow.strategy == ExecutionStrategy.SEQUENTIAL else set(),
                business_value=min(goal.level.value + 1, 5),
            )
            tasks.append(task)
            previous_id = task.task_id
        return tasks

    def _agent_for_phase(self, phase: str) -> str:
        phase_lower = phase.lower()
        if "research" in phase_lower or "scope" in phase_lower:
            return "Research Agent"
        if "knowledge" in phase_lower:
            return "Knowledge Agent"
        if "review" in phase_lower or "approval" in phase_lower:
            return "Guardian"
        if "publish" in phase_lower or "analytics" in phase_lower:
            return "Publishing Agent"
        if "architecture" in phase_lower or "task graph" in phase_lower:
            return "Development Agent"
        return "Content Agent"

    def _priority_for_goal(self, goal: Goal) -> Priority:
        if goal.level == PlanningLevel.STRATEGIC_OBJECTIVE:
            return Priority.CRITICAL
        if goal.level == PlanningLevel.INITIATIVE:
            return Priority.HIGH
        if goal.level == PlanningLevel.PROJECT:
            return Priority.MEDIUM
        return Priority.LOW

    def _get_plan(self, plan_id: str) -> ExecutionPlan:
        try:
            return self.plans[plan_id]
        except KeyError as exc:
            raise KeyError(f"Unknown plan_id: {plan_id}") from exc
