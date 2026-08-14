from dataclasses import replace

import pytest

from backend.content.adapters.memory import InMemoryContentRepository, RecordingEventPublisher
from backend.content.application.service import ContentService
from backend.content.domain.enums import (ClaimKind, ContentStatus, DuplicateDecision,
                                          FounderAction, ReviewStatus)
from backend.content.domain.errors import ApprovalError, ContentError, EvidenceError, InvalidTransition
from backend.content.domain.models import (Content, ContentBrief, ContentRequest, EvidenceClaim,
                                           RevisionRequest, SourceReference)
from backend.content.policies.disclaimers import assign_disclaimer
from backend.content.policies.transitions import transition


class Renderer:
    def render(self, content_request, brief):
        return f"{brief.main_insight}\n\nBased on available documentation."


class Detector:
    decision = DuplicateDecision.CREATE

    def evaluate(self, request, existing):
        self.existing = existing
        return self.decision


class Brand:
    def validate(self, content):
        assert "make you rich tomorrow" not in content.content_body


class Guardian:
    def __init__(self): self.requests = []
    def request_review(self, content): self.requests.append(content)


class Approval:
    def __init__(self): self.requests = []
    def request_founder_approval(self, content): self.requests.append(content)
    def get_action(self, content_id, version): return FounderAction.APPROVE


class Telegram:
    platform = "telegram"
    def adapt(self, body, brief): return f"TELEGRAM\n{body}\n{brief.cta}"


@pytest.fixture
def source():
    return SourceReference("S1", "https://example.test/source", "Primary documentation")


@pytest.fixture
def brief(source):
    claim = EvidenceClaim("C1", "The documented capability exists", ClaimKind.FACT,
                          ("S1",), ("R1",), ("K1",))
    return ContentBrief("AI tools", "New verified release", "Beginners", "Selection is hard",
                        "Use evidence before choosing", (claim,), "Educate", "telegram", "guide",
                        "calm and practical", "Save this workflow.", (source,), ("May change",))


@pytest.fixture
def content_request():
    return ContentRequest("AI tools", "Educate", "Beginners", "telegram", "tutorial", "content-agent",
                          workflow_id="WF-10")


@pytest.fixture
def system():
    repo, events, guardian, approval = (InMemoryContentRepository(), RecordingEventPublisher(),
                                        Guardian(), Approval())
    service = ContentService(repo, events, Renderer(), Detector(), Brand(), guardian, approval,
                             (Telegram(),))
    return service, repo, events, guardian, approval


def test_content_and_brief_validation(system, content_request, brief):
    item = system[0].create_draft(content_request, brief, .85)
    assert item.status is ContentStatus.DRAFT
    assert item.language == "ru" and item.metadata["visibility"] == "private"
    assert item.research_references == ("R1",) and item.knowledge_references == ("K1",)
    assert item.content_body.startswith("TELEGRAM")


def test_factual_claim_requires_traceable_source(source):
    claim = EvidenceClaim("C", "fact", ClaimKind.FACT)
    with pytest.raises(EvidenceError): claim.validate({source.source_id})
    unknown = replace(claim, source_ids=("missing",))
    with pytest.raises(EvidenceError): unknown.validate({source.source_id})


def test_test_result_cannot_be_invented(source):
    claim = EvidenceClaim("C", "we tested it", ClaimKind.TEST_RESULT, (source.source_id,))
    with pytest.raises(EvidenceError, match="experiment"):
        claim.validate({source.source_id})
    replace(claim, experiment_id="EXP-1").validate({source.source_id})


def test_version_history_is_immutable(system, content_request, brief):
    service, repo, *_ = system
    item = service.create_draft(content_request, brief, .9)
    with pytest.raises(ContentError, match="immutable"):
        repo.save_version(item)
    guardian_version = service.send_to_guardian(item.content_id)
    assert [v.version for v in repo.history(item.content_id)] == [1, 2]
    assert repo.get(item.content_id, 1).status is ContentStatus.DRAFT
    assert guardian_version.status is ContentStatus.GUARDIAN_REVIEW


def test_guardian_then_founder_are_mandatory(system, content_request, brief):
    service, repo, events, guardian, approval = system
    item = service.create_draft(content_request, brief, .9)
    with pytest.raises(ApprovalError): service.record_founder_action(item.content_id, FounderAction.APPROVE)
    pending = service.send_to_guardian(item.content_id)
    assert guardian.requests == [pending]
    founder = service.record_guardian_approval(item.content_id)
    assert founder.guardian_status is ReviewStatus.APPROVED and approval.requests == [founder]
    ready = service.record_founder_action(item.content_id, FounderAction.APPROVE)
    assert ready.status is ContentStatus.READY_TO_PUBLISH
    assert [e.name for e in events.events] == ["DraftCreated", "ContentSentToGuardian",
                                                "ContentApprovedByGuardian", "ContentReadyForPublishing"]
    assert len(repo.history(item.content_id)) == 4


def test_revision_creates_new_version(system, content_request, brief):
    service, repo, *_ = system
    item = service.create_draft(content_request, brief, .9)
    service.send_to_guardian(item.content_id)
    founder = service.record_guardian_approval(item.content_id)
    requested = service.record_founder_action(item.content_id, FounderAction.REQUEST_REVISION)
    revision = RevisionRequest("Clarify limitation", ("limitation",), "Founder",
                               original_version=requested.version, new_version=requested.version + 1)
    revised = service.revise(item.content_id, revision, "Revised body with limitation")
    assert revised.version == founder.version + 2
    assert revised.status is ContentStatus.DRAFT
    assert len(repo.history(item.content_id)) == 5


def test_status_policy_blocks_bypasses(system, content_request, brief):
    item = system[0].create_draft(content_request, brief, .9)
    with pytest.raises(InvalidTransition): transition(item, ContentStatus.FOUNDER_REVIEW)
    with pytest.raises(InvalidTransition): transition(item, ContentStatus.READY_TO_PUBLISH)
    with pytest.raises(ContentError, match="cannot mark"):
        replace(item, status=ContentStatus.PUBLISHED).validate()
    with pytest.raises(ContentError, match="approval"):
        replace(item, status=ContentStatus.READY_TO_PUBLISH).validate()


def test_duplicate_detector_can_skip(system, content_request, brief):
    service = system[0]
    service.duplicate_detector.decision = DuplicateDecision.SKIP
    with pytest.raises(ContentError, match="SKIP"):
        service.create_draft(content_request, brief, .8)


def test_disclaimer_assignment(source):
    claims = (EvidenceClaim("C", "test", ClaimKind.TEST_RESULT, ("S1",), experiment_id="E1"),)
    assert assign_disclaimer(claims, commercial=True) == "Commercial content; Experimental result"


def test_no_publishing_or_credentials_ports_exist():
    from backend.content.interfaces import ports
    assert not hasattr(ports, "PublishingGateway")
    assert not hasattr(ports, "CredentialProvider")
