from dataclasses import dataclass
from datetime import timedelta
from ..domain.models import FailureCategory, RECOVERABLE_FAILURES


@dataclass(frozen=True)
class RetryPolicy:
    maximum_attempts: int = 3
    base_backoff_seconds: int = 30

    def eligible(self, category: FailureCategory, attempts: int) -> bool:
        return category in RECOVERABLE_FAILURES and attempts < self.maximum_attempts

    def backoff(self, attempts: int) -> timedelta:
        return timedelta(seconds=self.base_backoff_seconds * (2 ** max(0, attempts - 1)))
