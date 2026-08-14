"""Permission-aware execution contracts and deterministic mock implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import StrEnum

from .models import TestCase, TestResult


class MockOutcome(StrEnum):
    SUCCESS = "successful"
    FAILED = "failed"
    TIMEOUT = "timeout"
    PARTIAL = "partial"
    INCONCLUSIVE = "inconclusive"
    HIGH_COST = "high_cost"
    INVALID_OUTPUT = "invalid_output"


class TestExecutor(ABC):
    @abstractmethod
    def execute(self, case: TestCase) -> TestResult: ...


class MockTestExecutor(TestExecutor):
    """Simulates every required outcome without external side effects."""

    def __init__(self, outcome: MockOutcome = MockOutcome.SUCCESS):
        self.outcome = outcome

    def execute(self, case: TestCase) -> TestResult:
        attempts = case.repeat_count
        mapping = {
            MockOutcome.SUCCESS: TestResult("SUCCESS", "mock output", {"quality": 1}, attempts=attempts),
            MockOutcome.FAILED: TestResult("FAILED", notes="mock failure", attempts=attempts, failures=attempts),
            MockOutcome.TIMEOUT: TestResult("TIMEOUT", notes="mock timeout", attempts=attempts, failures=attempts),
            MockOutcome.PARTIAL: TestResult("PARTIAL", "partial output", attempts=attempts, failures=max(1, attempts // 2)),
            MockOutcome.INCONCLUSIVE: TestResult("INCONCLUSIVE", notes="insufficient signal", attempts=attempts),
            MockOutcome.HIGH_COST: TestResult("BLOCKED", notes="cost boundary exceeded", attempts=0),
            MockOutcome.INVALID_OUTPUT: TestResult("INVALID", raw_vendor_result={"unexpected": True}, attempts=attempts, failures=attempts),
        }
        return mapping[self.outcome]
