from dataclasses import replace

from ..domain.enums import ContentStatus, FounderAction, ReviewStatus
from ..domain.errors import ApprovalError, ContentError
from ..domain.events import ContentEvent
from ..domain.models import Content, ContentBrief, ContentRequest, RevisionRequest, utcnow
from ..interfaces.ports import (ApprovalGateway, BrandPolicyProvider, ContentRenderer,
                                ContentRepository, DuplicateDetector, EventPublisher,
                                GuardianGateway, PlatformAdapter)
from ..policies.transitions import transition


class ContentService:
    def __init__(self, repository: ContentRepository, events: EventPublisher,
                 renderer: ContentRenderer, duplicate_detector: DuplicateDetector,
                 brand_policy: BrandPolicyProvider, guardian: GuardianGateway,
                 approval: ApprovalGateway, adapters: tuple[PlatformAdapter, ...] = ()) -> None:
        self.repository = repository
        self.events = events
        self.renderer = renderer
        self.duplicate_detector = duplicate_detector
        self.brand_policy = brand_policy
        self.guardian = guardian
        self.approval = approval
        self.adapters = {adapter.platform: adapter for adapter in adapters}

    def create_draft(self, request: ContentRequest, brief: ContentBrief, confidence: float) -> Content:
        brief.validate()
        decision = self.duplicate_detector.evaluate(request, self.repository.find_related(request.topic))
        if decision.value == "SKIP":
            raise ContentError("duplicate policy selected SKIP")
        body = self.renderer.render(request, brief)
        adapter = self.adapters.get(request.platform)
        if adapter:
            body = adapter.adapt(body, brief)
        content = Content.draft(request, brief, body, confidence)
        self.brand_policy.validate(content)
        self.repository.save_version(content)
        self.events.publish(ContentEvent("DraftCreated", content.content_id, request.workflow_id))
        return content

    def send_to_guardian(self, content_id: str) -> Content:
        content = transition(self.repository.get(content_id), ContentStatus.GUARDIAN_REVIEW)
        content = replace(content, guardian_status=ReviewStatus.PENDING)
        self.repository.save_version(replace(content, version=content.version + 1))
        current = self.repository.get(content_id)
        self.guardian.request_review(current)
        self.events.publish(ContentEvent("ContentSentToGuardian", content_id))
        return current

    def record_guardian_approval(self, content_id: str) -> Content:
        current = self.repository.get(content_id)
        if current.status is not ContentStatus.GUARDIAN_REVIEW:
            raise ApprovalError("content is not awaiting Guardian review")
        approved = replace(current, guardian_status=ReviewStatus.APPROVED,
                           updated_at=utcnow(), version=current.version + 1)
        approved = transition(approved, ContentStatus.FOUNDER_REVIEW)
        self.repository.save_version(approved)
        self.approval.request_founder_approval(approved)
        self.events.publish(ContentEvent("ContentApprovedByGuardian", content_id))
        return approved

    def record_founder_action(self, content_id: str, action: FounderAction) -> Content:
        current = self.repository.get(content_id)
        if current.status is not ContentStatus.FOUNDER_REVIEW:
            raise ApprovalError("content is not awaiting Founder review")
        if action is FounderAction.APPROVE:
            updated = replace(current, founder_approval_status=ReviewStatus.APPROVED,
                              updated_at=utcnow(), version=current.version + 1)
            updated = transition(updated, ContentStatus.APPROVED)
            updated = transition(updated, ContentStatus.READY_TO_PUBLISH)
            event = "ContentReadyForPublishing"
        elif action is FounderAction.REQUEST_REVISION:
            updated = replace(current, founder_approval_status=ReviewStatus.REVISION_REQUIRED,
                              status=ContentStatus.REVISION_REQUIRED, version=current.version + 1,
                              updated_at=utcnow())
            event = "RevisionRequested"
        elif action is FounderAction.REJECT:
            updated = replace(current, founder_approval_status=ReviewStatus.REJECTED,
                              status=ContentStatus.REJECTED, version=current.version + 1,
                              updated_at=utcnow())
            event = "ContentRejected"
        else:
            return current
        self.repository.save_version(updated)
        self.events.publish(ContentEvent(event, content_id))
        return updated

    def revise(self, content_id: str, revision: RevisionRequest, body: str) -> Content:
        current = self.repository.get(content_id)
        if current.status is not ContentStatus.REVISION_REQUIRED:
            raise ContentError("revision was not requested")
        revised = current.next_version(body=body, revision=revision)
        self.brand_policy.validate(revised)
        self.repository.save_version(revised)
        self.events.publish(ContentEvent("DraftUpdated", content_id,
                                         payload={"reviewer": revision.reviewer}))
        return revised
