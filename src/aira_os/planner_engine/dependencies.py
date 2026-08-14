"""Dependency validation and task ordering for Planner Engine plans."""

from __future__ import annotations

from collections import defaultdict, deque

from .models import DependencyIssue, Task


class DependencyEngine:
    """Validate dependencies and produce executable ordering without executing."""

    def validate(self, tasks: list[Task]) -> list[DependencyIssue]:
        issues: list[DependencyIssue] = []
        task_ids = {task.task_id for task in tasks}
        seen_titles: dict[str, str] = {}

        for task in tasks:
            normalized_title = task.title.strip().lower()
            if normalized_title in seen_titles:
                issues.append(
                    DependencyIssue(
                        "duplicate_task",
                        f"Task duplicates title of {seen_titles[normalized_title]}",
                        task.task_id,
                    )
                )
            seen_titles[normalized_title] = task.task_id

            for dependency in task.dependencies:
                if dependency not in task_ids:
                    issues.append(
                        DependencyIssue(
                            "missing_dependency",
                            f"Dependency {dependency} does not exist",
                            task.task_id,
                        )
                    )

        if self._has_cycle(tasks):
            issues.append(DependencyIssue("circular_dependency", "Task graph contains a cycle"))

        return issues

    def order(self, tasks: list[Task]) -> list[Task]:
        """Return dependency-safe task order, raising if the graph is invalid."""

        issues = self.validate(tasks)
        if any(issue.code in {"missing_dependency", "circular_dependency"} for issue in issues):
            details = "; ".join(issue.message for issue in issues)
            raise ValueError(f"Cannot order invalid dependency graph: {details}")

        by_id = {task.task_id: task for task in tasks}
        dependents: dict[str, list[str]] = defaultdict(list)
        indegree = {task.task_id: 0 for task in tasks}
        for task in tasks:
            for dependency in task.dependencies:
                dependents[dependency].append(task.task_id)
                indegree[task.task_id] += 1

        ready = deque(sorted(task_id for task_id, degree in indegree.items() if degree == 0))
        ordered: list[Task] = []
        while ready:
            task_id = ready.popleft()
            ordered.append(by_id[task_id])
            for dependent in sorted(dependents[task_id]):
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    ready.append(dependent)
        return ordered

    def _has_cycle(self, tasks: list[Task]) -> bool:
        task_ids = {task.task_id for task in tasks}
        visiting: set[str] = set()
        visited: set[str] = set()
        graph = {task.task_id: task.dependencies & task_ids for task in tasks}

        def visit(task_id: str) -> bool:
            if task_id in visiting:
                return True
            if task_id in visited:
                return False
            visiting.add(task_id)
            for dependency in graph[task_id]:
                if visit(dependency):
                    return True
            visiting.remove(task_id)
            visited.add(task_id)
            return False

        return any(visit(task_id) for task_id in graph)
