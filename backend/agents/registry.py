"""Authoritative, fail-closed agent and tool registries."""

from dataclasses import replace
from typing import Iterable

from .domain import (
    AgentManifest, AgentStatus, AgentType, AuditRecord, HealthMetrics, HealthStatus,
    Permission, ToolDefinition, utcnow,
)
from .prompts import PromptRegistry


TRANSITIONS = {
    AgentStatus.REGISTERED: {AgentStatus.INACTIVE},
    AgentStatus.INACTIVE: {AgentStatus.READY, AgentStatus.DISABLED, AgentStatus.RETIRED},
    AgentStatus.READY: {AgentStatus.BUSY, AgentStatus.PAUSED, AgentStatus.DEGRADED, AgentStatus.DISABLED},
    AgentStatus.BUSY: {AgentStatus.READY, AgentStatus.PAUSED, AgentStatus.DEGRADED, AgentStatus.ERROR},
    AgentStatus.PAUSED: {AgentStatus.READY, AgentStatus.DISABLED, AgentStatus.RETIRED},
    AgentStatus.DEGRADED: {AgentStatus.READY, AgentStatus.DISABLED, AgentStatus.ERROR},
    AgentStatus.ERROR: {AgentStatus.PAUSED, AgentStatus.DISABLED},
    AgentStatus.DISABLED: {AgentStatus.INACTIVE, AgentStatus.RETIRED},
    AgentStatus.RETIRED: set(),
}


class AgentRegistry:
    def __init__(self, prompts: PromptRegistry) -> None:
        self.prompts = prompts
        self._agents: dict[str, AgentManifest] = {}
        self._versions: dict[str, list[AgentManifest]] = {}
        self._tools: dict[str, ToolDefinition] = {}
        self._health: dict[str, HealthMetrics] = {}
        self.audit: list[AuditRecord] = []

    def register_tool(self, tool: ToolDefinition, actor: str = "control-plane") -> None:
        if tool.tool_id in self._tools or tool.calls_per_minute < 1:
            raise ValueError("duplicate or invalid tool")
        self._tools[tool.tool_id] = tool
        self.audit.append(AuditRecord("ToolRegistered", actor, None, details={"tool_id": tool.tool_id}))

    def register(self, manifest: AgentManifest, actor: str = "control-plane") -> AgentManifest:
        manifest.validate()
        if manifest.agent_id in self._agents:
            raise ValueError(f"duplicate agent id: {manifest.agent_id}")
        if not self.prompts.contains(manifest.prompt_id):
            raise ValueError(f"missing approved prompt: {manifest.prompt_id}")
        unknown_tools = manifest.tools - self._tools.keys()
        if unknown_tools:
            raise ValueError(f"unregistered tools: {sorted(unknown_tools)}")
        for tool_id in manifest.tools:
            tool = self._tools[tool_id]
            if manifest.agent_type not in tool.allowed_agent_types:
                raise ValueError(f"tool {tool_id} denies agent type")
            if not tool.required_permissions <= manifest.permissions:
                raise ValueError(f"tool {tool_id} permissions not satisfied")
        self._agents[manifest.agent_id] = manifest
        self._versions.setdefault(manifest.agent_id, []).append(manifest)
        self._health[manifest.agent_id] = HealthMetrics()
        self.audit.append(AuditRecord("AgentRegistered", actor, manifest.agent_id,
                                      details={"version": manifest.version}))
        return manifest

    def get(self, agent_id: str) -> AgentManifest:
        try:
            return self._agents[agent_id]
        except KeyError as exc:
            raise KeyError(f"unknown agent: {agent_id}") from exc

    def list(self, agent_type: AgentType | None = None) -> tuple[AgentManifest, ...]:
        values = self._agents.values()
        return tuple(a for a in values if agent_type is None or a.agent_type == agent_type)

    def transition(self, agent_id: str, status: AgentStatus, actor: str = "control-plane") -> AgentManifest:
        current = self.get(agent_id)
        if status not in TRANSITIONS[current.status]:
            raise ValueError(f"invalid lifecycle transition: {current.status} -> {status}")
        updated = replace(current, status=status, updated_at=utcnow())
        self._agents[agent_id] = updated
        self.audit.append(AuditRecord(f"Agent{status.value.title()}", actor, agent_id))
        return updated

    def activate(self, agent_id: str, actor: str = "control-plane") -> AgentManifest:
        agent = self.get(agent_id)
        if agent.status == AgentStatus.REGISTERED:
            self.transition(agent_id, AgentStatus.INACTIVE, actor)
        updated = self.transition(agent_id, AgentStatus.READY, actor)
        self._health[agent_id].state = HealthStatus.HEALTHY
        updated = replace(updated, health_status=HealthStatus.HEALTHY)
        self._agents[agent_id] = updated
        return updated

    def pause(self, agent_id: str, actor: str = "control-plane") -> AgentManifest:
        return self.transition(agent_id, AgentStatus.PAUSED, actor)

    def disable(self, agent_id: str, actor: str = "control-plane") -> AgentManifest:
        return self.transition(agent_id, AgentStatus.DISABLED, actor)

    def retire(self, agent_id: str, actor: str = "control-plane") -> AgentManifest:
        return self.transition(agent_id, AgentStatus.RETIRED, actor)

    def update_metadata(self, agent_id: str, *, description: str, actor: str = "control-plane") -> AgentManifest:
        current = self.get(agent_id)
        updated = replace(current, description=description, updated_at=utcnow())
        self._agents[agent_id] = updated
        self.audit.append(AuditRecord("AgentMetadataUpdated", actor, agent_id))
        return updated

    def add_version(self, manifest: AgentManifest, actor: str = "control-plane") -> None:
        current = self.get(manifest.agent_id)
        manifest.validate()
        if manifest.version in {a.version for a in self._versions[manifest.agent_id]}:
            raise ValueError("duplicate agent version")
        if manifest.status == AgentStatus.READY:
            raise ValueError("new version requires controlled activation")
        self._versions[manifest.agent_id].append(manifest)
        self.audit.append(AuditRecord("AgentVersionChanged", actor, manifest.agent_id,
                                      details={"from": current.version, "candidate": manifest.version}))

    def version_history(self, agent_id: str) -> tuple[AgentManifest, ...]:
        self.get(agent_id)
        return tuple(self._versions[agent_id])

    def health(self, agent_id: str) -> HealthMetrics:
        self.get(agent_id)
        return self._health[agent_id]

    def tool(self, tool_id: str) -> ToolDefinition:
        try:
            return self._tools[tool_id]
        except KeyError as exc:
            raise PermissionError(f"unregistered tool: {tool_id}") from exc

    def startup_validate(self) -> None:
        if len(self._agents) != len(set(self._agents)):
            raise RuntimeError("duplicate agents")
        for agent in self._agents.values():
            agent.validate()
            if not self.prompts.contains(agent.prompt_id):
                raise RuntimeError(f"missing prompt: {agent.prompt_id}")
            for tool in agent.tools:
                self.tool(tool)
