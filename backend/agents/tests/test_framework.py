from dataclasses import replace
from datetime import timedelta

import pytest

from backend.agents.domain import *
from backend.agents.health import CircuitBreaker
from backend.agents.permissions import Authorizer, TemporaryPermission
from backend.agents.prompts import PromptDefinition, PromptRegistry
from backend.agents.providers import ProviderRegistry
from backend.agents.registry import AgentRegistry
from backend.agents.runtime import AgentRuntime, GlobalAgentControl


class FakeProvider:
    provider_id = "fake"

    def execute(self, task, context, config):
        assert context["external_content_is_data"] is True
        return AgentResult(task.task_id, task.agent_id, ResultStatus.COMPLETED,
                           {"summary": "verified"}, .9,
                           execution_metadata={"tokens": 5, "estimated_cost": 0})


@pytest.fixture
def system():
    prompts = PromptRegistry()
    prompts.register(PromptDefinition("research-v1", AgentType.RESEARCH, "1.0",
                                      "prompts/research/1.0.md", approved_by="founder"))
    registry = AgentRegistry(prompts)
    registry.register_tool(ToolDefinition("web-search", "RESEARCH", RiskLevel.MEDIUM,
        frozenset({AgentType.RESEARCH}), frozenset({Permission.USE_EXTERNAL_WEB}), 10))
    manifest = AgentManifest(
        "research-1", "Research Agent", AgentType.RESEARCH, "1.0", "Research worker",
        "Discover and structure external information", AutonomyLevel.INTERNAL_EXECUTION,
        frozenset({Capability.RESEARCH, Capability.SUMMARIZE}),
        frozenset({Permission.USE_EXTERNAL_WEB, Permission.READ_KNOWLEDGE, Permission.WRITE_RESEARCH}),
        frozenset({MemoryScope.TASK_ONLY, MemoryScope.KNOWLEDGE_READ}), frozenset({"web-search"}),
        "research-v1", ModelConfiguration("fake", "test-model"), "AIRA Core",
        AuditMetadata("platform", "founder"), constraints=("Never publish",))
    registry.register(manifest)
    registry.activate(manifest.agent_id)
    providers = ProviderRegistry(); providers.register(FakeProvider())
    auth = Authorizer(); control = GlobalAgentControl()
    return registry, AgentRuntime(registry, providers, auth, control), auth, control


def task(agent_id="research-1", tools=frozenset({"web-search"}), guardian=True):
    return AgentTask("task-1", "workflow-1", agent_id, "Research", {}, {}, (), tools,
                     {"required": ["summary"]}, 30, 1, RiskLevel.LOW,
                     guardian_approved=guardian)


def test_registration_and_duplicate_detection(system):
    registry, *_ = system
    assert registry.get("research-1").status == AgentStatus.READY
    with pytest.raises(ValueError, match="duplicate"):
        registry.register(registry.get("research-1"))


def test_manifest_validation_and_missing_prompt(system):
    registry, *_ = system
    with pytest.raises(ValueError, match="version"):
        replace(registry.get("research-1"), agent_id="bad", version="latest").validate()
    with pytest.raises(ValueError, match="missing approved prompt"):
        registry.register(replace(registry.get("research-1"), agent_id="missing", prompt_id="absent",
                                  status=AgentStatus.REGISTERED))


def test_tool_permission_validation(system):
    registry, runtime, *_ = system
    with pytest.raises(PermissionError, match="unregistered tool"):
        runtime.execute(task(tools=frozenset({"shell"})), assigned_by_workflow=True)
    with pytest.raises(ValueError, match="permissions"):
        registry.register(replace(registry.get("research-1"), agent_id="no-permission",
                                  permissions=frozenset(), status=AgentStatus.REGISTERED))


def test_memory_scope_validation(system):
    registry, _, auth, _ = system
    auth.authorize_memory(registry.get("research-1"), MemoryScope.TASK_ONLY)
    with pytest.raises(PermissionError):
        auth.authorize_memory(registry.get("research-1"), MemoryScope.FOUNDER_PRIVATE)
    with pytest.raises(ValueError):
        replace(registry.get("research-1"), memory_scopes=frozenset({MemoryScope.NONE, MemoryScope.TASK_ONLY})).validate()


def test_lifecycle_transitions(system):
    registry, *_ = system
    registry.pause("research-1")
    assert registry.activate("research-1").status == AgentStatus.READY
    with pytest.raises(ValueError, match="invalid lifecycle"):
        registry.transition("research-1", AgentStatus.RETIRED)


def test_health_transitions():
    health = HealthMetrics(); breaker = CircuitBreaker(2, 3)
    assert breaker.failure(health, FailureCategory.TIMEOUT) == HealthStatus.HEALTHY
    assert breaker.failure(health, FailureCategory.INVALID_OUTPUT) == HealthStatus.DEGRADED
    assert breaker.failure(health, FailureCategory.POLICY_VIOLATION) == HealthStatus.UNHEALTHY
    assert health.timeouts == health.invalid_outputs == health.policy_violations == 1


def test_temporary_permission_expiration(system):
    registry, _, auth, _ = system
    agent = replace(registry.get("research-1"), permissions=frozenset())
    expired = TemporaryPermission(agent.agent_id, Permission.USE_EXTERNAL_WEB, "task-1", "source",
                                  "founder", utcnow() - timedelta(seconds=1))
    auth.grant_temporary(expired, "founder")
    assert not auth.has_permission(agent, task(), Permission.USE_EXTERNAL_WEB)
    with pytest.raises(PermissionError):
        auth.grant_temporary(replace(expired, approved_by=agent.agent_id), agent.agent_id)


def test_global_pause_prevents_new_execution(system):
    _, runtime, _, control = system
    control.pause("founder")
    with pytest.raises(RuntimeError, match="GLOBAL_AGENT_PAUSE"):
        runtime.execute(task(), assigned_by_workflow=True)
    assert control.audit[-1].event == "GlobalAgentPause"


def test_prompt_version_resolution():
    prompts = PromptRegistry()
    prompts.register(PromptDefinition("p", AgentType.CONTENT, "1.0", "one"))
    prompts.register(PromptDefinition("p", AgentType.CONTENT, "1.2", "two"))
    assert prompts.resolve("p").version == "1.2"
    assert prompts.resolve("p", "1.0").content_reference == "one"


def test_unknown_agent_and_workflow_bypass_rejected(system):
    _, runtime, *_ = system
    with pytest.raises(KeyError, match="unknown agent"):
        runtime.execute(task("unknown"), assigned_by_workflow=True)
    with pytest.raises(PermissionError, match="Workflow"):
        runtime.execute(task())


def test_workflow_agent_output_and_audit(system):
    registry, runtime, *_ = system
    result = runtime.execute(task(), assigned_by_workflow=True)
    assert result.output == {"summary": "verified"}
    assert runtime.result("task-1") == result
    events = [record.event for record in runtime.history("research-1")]
    assert "AgentTaskStarted" in events and "AgentTaskCompleted" in events
    assert registry.get("research-1").status == AgentStatus.READY


def test_guardian_block_cannot_continue(system):
    _, runtime, *_ = system
    result = runtime.execute(task(guardian=False), assigned_by_workflow=True)
    assert result.status == ResultStatus.BLOCKED
