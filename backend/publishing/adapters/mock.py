from enum import StrEnum
from ..domain.models import *


class MockBehavior(StrEnum):
    SUCCESS = "SUCCESS"
    NETWORK_FAILURE = "NETWORK_FAILURE"
    RATE_LIMIT = "RATE_LIMIT"
    AUTHENTICATION_FAILURE = "AUTHENTICATION_FAILURE"
    PLATFORM_REJECTION = "PLATFORM_REJECTION"
    TIMEOUT = "TIMEOUT"
    DUPLICATE_REQUEST = "DUPLICATE_REQUEST"


class MockPlatformAdapter:
    """Non-production adapter with controllable failure modes."""
    name = "mock"

    def __init__(self, behavior=MockBehavior.SUCCESS):
        self.behavior, self.calls, self._results = behavior, 0, {}

    def validate(self, publication, content):
        if publication.platform != "mock":
            raise AdapterError("unsupported platform", FailureCategory.VALIDATION_ERROR)

    def prepare(self, publication, content):
        return {"publication": publication, "content": content}

    def publish(self, prepared, idempotency_key):
        self.calls += 1
        if idempotency_key in self._results:
            return self._results[idempotency_key]
        categories = {
            MockBehavior.NETWORK_FAILURE: FailureCategory.NETWORK_ERROR,
            MockBehavior.TIMEOUT: FailureCategory.NETWORK_ERROR,
            MockBehavior.RATE_LIMIT: FailureCategory.RATE_LIMIT,
            MockBehavior.AUTHENTICATION_FAILURE: FailureCategory.AUTHENTICATION_ERROR,
            MockBehavior.PLATFORM_REJECTION: FailureCategory.PLATFORM_ERROR,
        }
        if self.behavior in categories:
            raise AdapterError(self.behavior.value, categories[self.behavior])
        if self.behavior == MockBehavior.DUPLICATE_REQUEST:
            raise AdapterError("duplicate", FailureCategory.VALIDATION_ERROR)
        publication = prepared["publication"]
        content = prepared["content"]
        result = AdapterResult(f"mock-{publication.publication_id}", content.checksum,
                               {"simulation": True}, f"https://mock.invalid/{publication.publication_id}")
        self._results[idempotency_key] = result
        return result

    def health_check(self): return True
    def schedule(self, *args): raise UnsupportedOperation("mock scheduling is unsupported")
    def delete(self, *args): raise UnsupportedOperation("deletion requires a dedicated approved workflow")

