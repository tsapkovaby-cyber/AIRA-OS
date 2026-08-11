"""Least-privilege authorization, including task-bound temporary grants."""

from dataclasses import dataclass, field
from datetime import datetime

from .domain import AgentManifest, AgentTask, MemoryScope, Permission, ToolDefinition, utcnow


@dataclass(frozen=True)
class TemporaryPermission:
    agent_id: str
    permission: Permission
    task_id: str
    reason: str
    approved_by: str
    expires_at: datetime | None = None
    used: bool = False

    def active_for(self, agent_id: str, task_id: str, now: datetime | None = None) -> bool:
        now = now or utcnow()
        return (not self.used and self.agent_id == agent_id and self.task_id == task_id
                and (self.expires_at is None or now < self.expires_at))


class Authorizer:
    def __init__(self) -> None:
        self._temporary: list[TemporaryPermission] = []

    def grant_temporary(self, grant: TemporaryPermission, actor: str) -> None:
        if actor != grant.approved_by or actor == grant.agent_id:
            raise PermissionError("agents cannot grant their own permissions")
        self._temporary.append(grant)

    def has_permission(self, agent: AgentManifest, task: AgentTask, permission: Permission) -> bool:
        return permission in agent.permissions or any(
            g.permission == permission and g.active_for(agent.agent_id, task.task_id)
            for g in self._temporary
        )

    def authorize_tool(self, agent: AgentManifest, task: AgentTask, tool: ToolDefinition) -> None:
        if tool.tool_id not in agent.tools or tool.tool_id not in task.allowed_tools:
            raise PermissionError("tool is outside agent or task scope")
        if agent.agent_type not in tool.allowed_agent_types:
            raise PermissionError("agent type is forbidden for tool")
        if not all(self.has_permission(agent, task, p) for p in tool.required_permissions):
            raise PermissionError("required tool permission missing")

    @staticmethod
    def authorize_memory(agent: AgentManifest, requested: MemoryScope) -> None:
        if requested not in agent.memory_scopes or requested == MemoryScope.NONE:
            raise PermissionError(f"memory scope denied: {requested.value}")
