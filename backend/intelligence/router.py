from __future__ import annotations

from .domain import *
from .providers import IntelligenceProvider


class ModelRouter:
    def __init__(self, providers: dict[str, IntelligenceProvider], profiles: list[ModelProfile], tasks: list[TaskProfile]):
        self.providers = providers
        self.profiles = {p.profile_id: p for p in profiles}
        self.tasks = {t.profile_id: t for t in tasks}
        self.policy = RoutingPolicy.BALANCED
        self.disabled_providers: set[str] = set()

    def set_policy(self, policy: RoutingPolicy): self.policy = policy
    def get_available_profiles(self): return tuple(p for p in self.profiles.values() if self._available(p))
    def get_provider_health(self): return {name: provider.health_check() for name, provider in self.providers.items()}
    def get_fallback_chain(self, profile_id): return self.profiles[profile_id].fallback_profiles
    def disable_provider(self, provider): self.disabled_providers.add(provider)

    def _available(self, p):
        return (p.status == "ACTIVE" and p.provider not in self.disabled_providers and p.provider in self.providers
                and self.providers[p.provider].health_check().state == HealthState.HEALTHY)

    def _candidates(self, request):
        task = self.tasks[request.task_profile]
        rank = list(Sensitivity).index
        return [p for p in self.profiles.values() if self._available(p)
                and task.required_capabilities <= p.capabilities and request.context_tokens <= p.context_limit
                and p.reliability >= task.minimum_reliability
                and rank(task.sensitivity) <= rank(p.allowed_sensitivity)
                and (task.maximum_latency_ms is None or p.latency_ms <= task.maximum_latency_ms)
                and (task.maximum_cost is None or self.estimate_task_cost(request, p.profile_id) <= task.maximum_cost)]

    def estimate_task_cost(self, request, profile_id):
        p = self.profiles[profile_id]
        return p.cost.estimate(request.input_tokens, request.expected_output_tokens)

    def route_task(self, request):
        task, candidates = self.tasks[request.task_profile], self._candidates(request)
        if not candidates:
            raise LookupError("no safe model profile satisfies task requirements")
        policy = task.policy if task.policy != RoutingPolicy.BALANCED else self.policy
        if policy == RoutingPolicy.FOUNDER_SELECTED and request.founder_preference:
            candidates.sort(key=lambda p: p.profile_id != request.founder_preference)
        elif policy == RoutingPolicy.LOW_COST:
            candidates.sort(key=lambda p: self.estimate_task_cost(request, p.profile_id))
        elif policy == RoutingPolicy.LOW_LATENCY:
            candidates.sort(key=lambda p: p.latency_ms)
        elif policy in (RoutingPolicy.QUALITY_FIRST, RoutingPolicy.CRITICAL_REVIEW):
            candidates.sort(key=lambda p: (-p.evaluation_scores.get(task.profile_id, p.reliability * 100), -p.reliability))
        else:
            candidates.sort(key=lambda p: (self.estimate_task_cost(request, p.profile_id), p.latency_ms, -p.reliability))
        selected = candidates[0]
        fallback = tuple(x for x in selected.fallback_profiles if x in {p.profile_id for p in candidates}) if task.fallback_allowed else ()
        return RouteDecision(selected.provider, selected.profile_id, fallback,
            self.estimate_task_cost(request, selected.profile_id), selected.latency_ms,
            f"Meets {', '.join(sorted(task.required_capabilities))}; policy={policy}", selected.reliability,
            tuple(p.profile_id for p in candidates[1:]))

    def explain_routing(self, request):
        decision = self.route_task(request)
        return {"requirements": sorted(self.tasks[request.task_profile].required_capabilities), "selected": decision.model_profile,
                "alternatives": decision.alternatives, "cost": decision.expected_cost, "reason": decision.reason,
                "fallback": decision.fallback_chain}

