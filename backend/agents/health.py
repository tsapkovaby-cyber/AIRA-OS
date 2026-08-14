"""Health tracking and deterministic circuit-breaker policy."""

from .domain import FailureCategory, HealthMetrics, HealthStatus, utcnow


class CircuitBreaker:
    def __init__(self, degrade_after: int = 3, disable_after: int = 5) -> None:
        if not 0 < degrade_after < disable_after:
            raise ValueError("circuit breaker thresholds are invalid")
        self.degrade_after = degrade_after
        self.disable_after = disable_after

    def success(self, metrics: HealthMetrics, latency_ms: float) -> HealthStatus:
        metrics.total_tasks += 1
        metrics.last_successful_task = utcnow()
        metrics.heartbeat = utcnow()
        metrics.average_latency_ms += (latency_ms - metrics.average_latency_ms) / metrics.total_tasks
        metrics.state = HealthStatus.HEALTHY if metrics.failures < self.degrade_after else HealthStatus.DEGRADED
        return metrics.state

    def failure(self, metrics: HealthMetrics, category: FailureCategory) -> HealthStatus:
        metrics.total_tasks += 1
        metrics.failures += 1
        metrics.heartbeat = utcnow()
        if category == FailureCategory.INVALID_OUTPUT:
            metrics.invalid_outputs += 1
        elif category == FailureCategory.TOOL_ERROR:
            metrics.tool_errors += 1
        elif category == FailureCategory.TIMEOUT:
            metrics.timeouts += 1
        elif category in (FailureCategory.PERMISSION_DENIED, FailureCategory.POLICY_VIOLATION):
            metrics.policy_violations += 1
        metrics.state = (HealthStatus.UNHEALTHY if metrics.failures >= self.disable_after
                         else HealthStatus.DEGRADED if metrics.failures >= self.degrade_after
                         else HealthStatus.HEALTHY)
        return metrics.state
