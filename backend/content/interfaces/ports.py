from __future__ import annotations

from typing import Any, Protocol, Sequence

from ..domain.enums import DuplicateDecision, FounderAction
from ..domain.events import ContentEvent
from ..domain.models import Content, ContentBrief, ContentRequest


class ContentRepository(Protocol):
    def save_version(self, content: Content) -> None: ...
    def get(self, content_id: str, version: int | None = None) -> Content: ...
    def history(self, content_id: str) -> Sequence[Content]: ...
    def find_related(self, topic: str) -> Sequence[Content]: ...


class KnowledgeReader(Protocol):
    def search(self, topic: str) -> Sequence[Any]: ...


class ResearchReader(Protocol):
    def search_verified(self, topic: str) -> Sequence[Any]: ...


class MemoryReader(Protocol):
    def find_experiment(self, experiment_id: str) -> Any | None: ...


class BrandPolicyProvider(Protocol):
    def validate(self, content: Content) -> None: ...


class GuardianGateway(Protocol):
    def request_review(self, content: Content) -> None: ...


class ApprovalGateway(Protocol):
    def request_founder_approval(self, content: Content) -> None: ...
    def get_action(self, content_id: str, version: int) -> FounderAction: ...


class EventPublisher(Protocol):
    def publish(self, event: ContentEvent) -> None: ...


class ContentRenderer(Protocol):
    def render(self, request: ContentRequest, brief: ContentBrief) -> str: ...


class PlatformAdapter(Protocol):
    @property
    def platform(self) -> str: ...
    def adapt(self, body: str, brief: ContentBrief) -> str: ...


class AIProvider(Protocol):
    """Provider-neutral generation boundary; implementations live outside Core."""
    @property
    def provider_name(self) -> str: ...
    def generate(self, *, instructions: str, context: str) -> str: ...


class DuplicateDetector(Protocol):
    def evaluate(self, request: ContentRequest, existing: Sequence[Content]) -> DuplicateDecision: ...
