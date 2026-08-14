from dataclasses import replace

from ..domain.enums import ContentStatus, ReviewStatus
from ..domain.errors import InvalidTransition
from ..domain.models import Content, utcnow

_ALLOWED = {
    ContentStatus.IDEA: {ContentStatus.RESEARCH_REQUIRED, ContentStatus.BRIEF, ContentStatus.REJECTED},
    ContentStatus.RESEARCH_REQUIRED: {ContentStatus.BRIEF, ContentStatus.REJECTED},
    ContentStatus.BRIEF: {ContentStatus.DRAFT, ContentStatus.RESEARCH_REQUIRED},
    ContentStatus.DRAFT: {ContentStatus.GUARDIAN_REVIEW, ContentStatus.ARCHIVED},
    ContentStatus.REVISION_REQUIRED: {ContentStatus.DRAFT, ContentStatus.REJECTED},
    ContentStatus.GUARDIAN_REVIEW: {ContentStatus.REVISION_REQUIRED, ContentStatus.FOUNDER_REVIEW, ContentStatus.REJECTED},
    ContentStatus.FOUNDER_REVIEW: {ContentStatus.REVISION_REQUIRED, ContentStatus.APPROVED, ContentStatus.REJECTED},
    ContentStatus.APPROVED: {ContentStatus.READY_TO_PUBLISH, ContentStatus.ARCHIVED},
    ContentStatus.READY_TO_PUBLISH: {ContentStatus.ARCHIVED},
    ContentStatus.REJECTED: {ContentStatus.ARCHIVED},
    ContentStatus.ARCHIVED: set(),
}


def transition(content: Content, target: ContentStatus) -> Content:
    if target not in _ALLOWED.get(content.status, set()):
        raise InvalidTransition(f"cannot transition {content.status} to {target}")
    if target is ContentStatus.FOUNDER_REVIEW and content.guardian_status is not ReviewStatus.APPROVED:
        raise InvalidTransition("Guardian approval is required before Founder review")
    if target in {ContentStatus.APPROVED, ContentStatus.READY_TO_PUBLISH} and (
        content.guardian_status is not ReviewStatus.APPROVED
        or content.founder_approval_status is not ReviewStatus.APPROVED
    ):
        raise InvalidTransition("both approvals are required")
    result = replace(content, status=target, updated_at=utcnow())
    result.validate()
    return result
