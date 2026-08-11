from datetime import datetime, timezone
import pytest

from backend.publishing.application.service import PublishingService
from backend.publishing.adapters.mock import MockPlatformAdapter, MockBehavior
from backend.publishing.domain.models import *
from backend.publishing.policies.approval import StrictApprovalValidator
from backend.publishing.queue.memory import InMemoryPublishingQueue


class Store:
    def __init__(self, values=None): self.values = values or {}
    def get(self, key): return self.values.get(key)
    def save(self, value): self.values[value.publication_id] = value
    def append(self, value): self.values.setdefault("events", []).append(value)

class Events:
    def __init__(self): self.items = []
    def publish(self, name, payload): self.items.append((name, payload))

class Credentials:
    def is_available(self, reference): return reference == "secret://mock/account"

class Idempotency:
    def __init__(self): self.claims, self.receipts = {}, {}
    def claim(self, key, publication_id):
        if key in self.claims and self.claims[key] != publication_id: return False
        self.claims[key] = publication_id; return True
    def complete(self, key, receipt): self.receipts[key] = receipt
    def receipt(self, key): return self.receipts.get(key)

class Clock:
    def now(self): return datetime(2026, 8, 10, tzinfo=timezone.utc)


def setup(behavior=MockBehavior.SUCCESS, version=3, guardian=ApprovalStatus.APPROVED,
          founder=ApprovalStatus.APPROVED, media=None):
    content = ContentSnapshot("c1", version, ContentStatus.READY_TO_PUBLISH, "sha256:ok", ("a1",) if media else ())
    approvals = lambda status, ident: Approval(ident, status, "c1", 3)
    repo, queue, adapter, audit, events, idem = Store(), InMemoryPublishingQueue(), MockPlatformAdapter(behavior), Store(), Events(), Idempotency()
    service = PublishingService(repository=repo, queue=queue, content=Store({"c1": content}),
        accounts=Store({"acct": Account("acct", "mock", "Mock", "external", "secret://mock/account", frozenset({"PUBLISHER"}))}),
        approval_validator=StrictApprovalValidator({"g": approvals(guardian, "g")}, {"f": approvals(founder, "f")}),
        media_repository=Store({"a1": media} if media else {}), credentials=Credentials(), audit=audit,
        events=events, idempotency=idem, adapters={"mock": adapter}, clock=Clock())
    publication = Publication("p1", "c1", version, "w1", "mock", "acct", "TEXT", "g", "f", "idem-1", "mock", Clock().now())
    return service, publication, repo, queue, adapter, audit, events


def test_approved_lifecycle_creates_receipt_and_audit():
    service, publication, repo, queue, adapter, audit, events = setup()
    service.enqueue(publication)
    receipt = service.process(queue.next())
    assert receipt.external_id == "mock-p1"
    assert repo.get("p1").status == PublicationStatus.PUBLISHED
    assert {e.event_type for e in audit.values["events"]} >= {"PublicationQueued", "PublicationStarted", "PublicationSucceeded"}

@pytest.mark.parametrize("guardian,founder", [(ApprovalStatus.REJECTED, ApprovalStatus.APPROVED), (ApprovalStatus.APPROVED, ApprovalStatus.PENDING)])
def test_invalid_approval_is_blocked_and_audited(guardian, founder):
    service, publication, repo, queue, *_ = setup(guardian=guardian, founder=founder)
    with pytest.raises(ValidationError): service.enqueue(publication)
    assert publication.status == PublicationStatus.NOT_APPROVED
    assert queue.next() is None

def test_modified_content_cannot_reuse_old_approval():
    service, publication, *_ = setup(version=4)
    with pytest.raises(ValidationError, match="version"): service.enqueue(publication)

def test_idempotency_returns_receipt_without_second_external_post():
    service, publication, _, queue, adapter, *_ = setup()
    service.enqueue(publication); first = service.process(queue.next()); second = service.process("p1")
    assert first == second and adapter.calls == 1

def test_cancellation_prevents_processing():
    service, publication, _, queue, *_ = setup()
    service.enqueue(publication); service.cancel("p1")
    assert queue.next() is None
    with pytest.raises(ValidationError): service.process("p1")

def test_recoverable_failure_retries_but_authentication_does_not():
    service, publication, repo, queue, *_ = setup(MockBehavior.NETWORK_FAILURE)
    service.enqueue(publication)
    with pytest.raises(AdapterError): service.process(queue.next())
    assert repo.get("p1").status == PublicationStatus.RETRYING
    service2, pub2, repo2, queue2, *_ = setup(MockBehavior.AUTHENTICATION_FAILURE)
    service2.enqueue(pub2)
    with pytest.raises(AdapterError): service2.process(queue2.next())
    assert repo2.get("p1").status == PublicationStatus.FAILED

def test_maximum_retries_creates_failed_incident():
    service, publication, repo, queue, *_ = setup(MockBehavior.RATE_LIMIT)
    service.enqueue(publication)
    for _ in range(3):
        with pytest.raises(AdapterError): service.process(queue.next())
    assert repo.get("p1").status == PublicationStatus.FAILED
    assert repo.get("p1").audit_history[-1].details["incident"] is True

def test_emergency_pause_blocks_publication_then_resume_continues():
    service, publication, repo, queue, *_ = setup()
    service.enqueue(publication); service.set_global_pause(True, "founder")
    assert queue.next() is None
    service.set_global_pause(False, "founder")
    assert service.process(queue.next()).external_id == "mock-p1"

def test_media_version_and_approval_are_verified():
    bad = MediaAsset("a1", "c1", 2, "checksum", "png", True)
    service, publication, _, queue, *_ = setup(media=bad)
    service.enqueue(publication)
    with pytest.raises(ValidationError, match="media integrity"): service.process(queue.next())

def test_external_deletion_never_occurs_without_founder_approval():
    service, publication, *_ = setup()
    with pytest.raises(ValidationError, match="Founder"): service.delete_external("p1")
    with pytest.raises(UnsupportedOperation): service.delete_external("p1", founder_approval_id="delete-approval")

def test_queue_pause_resume_and_duplicate_enqueue():
    queue = InMemoryPublishingQueue(); queue.enqueue("p1"); queue.enqueue("p1"); queue.pause()
    assert queue.next() is None
    queue.resume(); assert queue.next() == "p1" and queue.next() is None

