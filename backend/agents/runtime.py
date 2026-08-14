"""Workflow-only runtime enforcing registry, Guardian, tool, and audit boundaries."""

from dataclasses import replace
from time import monotonic

from .domain import (
    AgentResult, AgentStatus, AgentTask, AuditRecord, FailureCategory, HealthStatus,
    ResultStatus, utcnow,
)
from .health import CircuitBreaker
from .permissions import Authorizer
from .providers import ProviderRegistry
from .registry import AgentRegistry, TRANSITIONS


class GlobalAgentControl:
    def __init__(self) -> None:
        self.paused = False
        self.audit: list[AuditRecord] = []

    def pause(self, actor: str) -> None:
        self.paused = True
        self.audit.append(AuditRecord("GlobalAgentPause", actor, None))

    def resume(self, actor: str) -> None:
        self.paused = False
        self.audit.append(AuditRecord("GlobalAgentResume", actor, None))


class AgentRuntime:
    def __init__(self, registry: AgentRegistry, providers: ProviderRegistry,
                 authorizer: Authorizer, control: GlobalAgentControl,
                 circuit_breaker: CircuitBreaker | None = None) -> None:
        self.registry = registry
        self.providers = providers
        self.authorizer = authorizer
        self.control = control
        self.breaker = circuit_breaker or CircuitBreaker()
        self._results: dict[str, AgentResult] = {}
        self._cancelled: set[str] = set()

    def execute(self, task: AgentTask, *, assigned_by_workflow: bool = False) -> AgentResult:
        if not assigned_by_workflow:
            raise PermissionError("agents execute only through Workflow")
        if self.control.paused:
            raise RuntimeError("GLOBAL_AGENT_PAUSE is active")
        agent = self.registry.get(task.agent_id)  # unknown agents fail closed
        if agent.status != AgentStatus.READY:
            raise RuntimeError(f"agent is unavailable: {agent.status.value}")
        if not task.guardian_approved:
            result = AgentResult(task.task_id, agent.agent_id, ResultStatus.BLOCKED, {}, 0,
                                 errors=("Guardian blocked execution",))
            self._results[task.task_id] = result
            return result
        for tool_id in task.allowed_tools:
            self.authorizer.authorize_tool(agent, task, self.registry.tool(tool_id))
        if task.timeout_seconds > agent.timeout_seconds:
            raise ValueError("task timeout exceeds agent limit")
        self.registry.transition(agent.agent_id, AgentStatus.BUSY, "workflow")
        started = utcnow()
        tick = monotonic()
        self.registry.audit.append(AuditRecord("AgentTaskStarted", "workflow", agent.agent_id,
                                               task.workflow_id, task.task_id,
                                               {"version": agent.version, "tools": sorted(task.allowed_tools),
                                                "provider": agent.model_profile.provider}))
        try:
            if task.task_id in self._cancelled:
                raise RuntimeError("task cancelled")
            provider = self.providers.get(agent.model_profile.provider)
            safe_context = {"task_context": dict(task.context), "constraints": task.constraints,
                            "external_content_is_data": True,
                            "tools": sorted(task.allowed_tools), "expected_output": task.expected_output}
            result = provider.execute(task, safe_context, agent.model_profile)
            if result.task_id != task.task_id or result.agent_id != agent.agent_id:
                raise ValueError("invalid provider output contract")
            self._results[task.task_id] = result
            self.breaker.success(self.registry.health(agent.agent_id), (monotonic() - tick) * 1000)
            self.registry.transition(agent.agent_id, AgentStatus.READY, "workflow")
            self.registry.audit.append(AuditRecord("AgentTaskCompleted", "workflow", agent.agent_id,
                                                   task.workflow_id, task.task_id,
                                                   {"confidence": result.confidence, "result": result.status.value,
                                                    "started_at": started.isoformat(), "ended_at": utcnow().isoformat()}))
            return result
        except Exception as exc:
            state = self.breaker.failure(self.registry.health(agent.agent_id), FailureCategory.UNKNOWN_FAILURE)
            target = AgentStatus.DEGRADED if state == HealthStatus.DEGRADED else AgentStatus.ERROR
            if target in TRANSITIONS[self.registry.get(agent.agent_id).status]:
                self.registry.transition(agent.agent_id, target, "circuit-breaker")
            self.registry.audit.append(AuditRecord("AgentTaskFailed", "runtime", agent.agent_id,
                                                   task.workflow_id, task.task_id, {"error": str(exc)}))
            raise

    def cancel(self, task_id: str, actor: str = "workflow") -> None:
        self._cancelled.add(task_id)
        self.registry.audit.append(AuditRecord("AgentTaskCancelled", actor, None, task_id=task_id))

    def result(self, task_id: str) -> AgentResult:
        return self._results[task_id]

    def history(self, agent_id: str) -> tuple[AuditRecord, ...]:
        self.registry.get(agent_id)
        return tuple(r for r in self.registry.audit if r.agent_id == agent_id)

    def health_check(self, agent_id: str):
        return self.registry.health(agent_id)
