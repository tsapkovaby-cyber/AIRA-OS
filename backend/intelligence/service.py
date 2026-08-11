from __future__ import annotations

import time
import uuid
from dataclasses import asdict

from .domain import InferenceResult, ProviderError, ProviderErrorCode, RoutingRequest


class BudgetExceeded(RuntimeError): pass


class BudgetLedger:
    def __init__(self, task_limit=None, project_limit=None, warning_ratio=.8):
        self.task_limit, self.project_limit, self.warning_ratio = task_limit, project_limit, warning_ratio
        self.spent = 0.0

    def authorize(self, estimate):
        limit = min(x for x in (self.task_limit, self.project_limit) if x is not None) if any(x is not None for x in (self.task_limit, self.project_limit)) else None
        if limit is not None and self.spent + estimate > limit:
            raise BudgetExceeded("inference budget exceeded")

    def record(self, cost): self.spent += cost


class AuditLog:
    def __init__(self): self.records = []
    def append(self, event, **data): self.records.append({"event": event, **data})


class IntelligenceService:
    FALLBACK_ERRORS = {ProviderErrorCode.TIMEOUT, ProviderErrorCode.RATE_LIMIT, ProviderErrorCode.UNAVAILABLE,
                       ProviderErrorCode.CONTENT_ERROR, ProviderErrorCode.UNKNOWN}

    def __init__(self, router, validator, budget=None, audit=None):
        self.router, self.validator = router, validator
        self.budget, self.audit = budget or BudgetLedger(), audit or AuditLog()

    def execute(self, request: RoutingRequest, prompt, schema=None):
        inference_id, started = str(uuid.uuid4()), time.monotonic()
        decision = self.router.route_task(request)
        self.budget.authorize(decision.expected_cost)
        self.audit.append("InferenceRequested", inference_id=inference_id, task_id=request.task_id,
                          workflow_id=request.workflow_id, agent_id=request.agent_id)
        self.audit.append("ModelRouted", inference_id=inference_id, **asdict(decision))
        chain, last_error = (decision.model_profile,) + decision.fallback_chain, None
        for attempt, profile_id in enumerate(chain, 1):
            profile = self.router.profiles[profile_id]
            provider = self.router.providers[profile.provider]
            try:
                self.audit.append("InferenceStarted", inference_id=inference_id, provider=profile.provider, model_profile=profile_id)
                raw = provider.generate(prompt, profile.model_id)
                content = self.validator.validate(raw, schema) if schema else raw
                cost = profile.cost.estimate(request.input_tokens, request.expected_output_tokens)
                self.budget.record(cost)
                self.audit.append("InferenceCompleted", inference_id=inference_id, model_profile=profile_id,
                                  duration_ms=(time.monotonic()-started)*1000, cost=cost, validation="valid")
                return InferenceResult(inference_id, content, profile_id, attempt > 1, cost, attempt)
            except (ProviderError, ValueError) as exc:
                last_error = exc
                allowed = isinstance(exc, ValueError) or exc.code in self.FALLBACK_ERRORS
                self.audit.append("InferenceFailed", inference_id=inference_id, model_profile=profile_id, error=type(exc).__name__)
                if attempt < len(chain) and allowed:
                    self.audit.append("FallbackTriggered", inference_id=inference_id, from_profile=profile_id)
                    continue
                raise
        raise last_error

