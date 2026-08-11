"""Approval-gated publishing use cases; no editorial operations exist here."""
from __future__ import annotations
from threading import Lock
from ..domain.models import *
from ..policies.retry import RetryPolicy


class PublishingService:
    def __init__(self, *, repository, queue, content, accounts, approval_validator,
                 media_repository, credentials, audit, events, idempotency, adapters,
                 clock, retry_policy=RetryPolicy()):
        self.repo, self.queue, self.content, self.accounts = repository, queue, content, accounts
        self.approvals, self.media, self.credentials = approval_validator, media_repository, credentials
        self.audit, self.events, self.idempotency, self.adapters = audit, events, idempotency, adapters
        self.clock, self.retry_policy, self.global_pause = clock, retry_policy, False
        self._locks: dict[str, Lock] = {}

    def _record(self, publication, event_type, **details):
        event = AuditEvent(event_type, publication.publication_id, self.clock.now(), details)
        publication.audit_history.append(event); publication.updated_at = event.timestamp
        self.audit.append(event); self.events.publish(event_type, {"publication_id": publication.publication_id, **details})

    def enqueue(self, publication: Publication):
        try:
            snapshot = self.content.get(publication.content_id)
            if snapshot is None: raise ValidationError("content does not exist")
            self.approvals.validate(publication, snapshot)
            account = self.accounts.get(publication.account_id)
            if not account or not account.enabled or account.platform != publication.platform:
                raise ValidationError("destination account is unavailable")
            if not ({"OWNER", "ADMIN", "PUBLISHER"} & account.permissions):
                raise ValidationError("account lacks publishing permission")
        except ValidationError as error:
            publication.status = PublicationStatus.NOT_APPROVED
            self._record(publication, "PublicationBlocked", reason=str(error))
            self.repo.save(publication)
            raise
        publication.status = PublicationStatus.SCHEDULED if publication.scheduled_at_utc else PublicationStatus.QUEUED
        self._record(publication, "GuardianApprovalValidated")
        self._record(publication, "FounderApprovalValidated")
        self._record(publication, "PublicationScheduled" if publication.scheduled_at_utc else "PublicationQueued")
        self.repo.save(publication); self.queue.enqueue(publication.publication_id, publication.scheduled_at_utc)

    def preflight(self, publication):
        if self.global_pause: raise ValidationError("global publishing pause is enabled")
        if publication.status == PublicationStatus.CANCELLED: raise ValidationError("publication is cancelled")
        if publication.status == PublicationStatus.PUBLISHED: raise ValidationError("publication is already published")
        snapshot = self.content.get(publication.content_id)
        if snapshot is None: raise ValidationError("content does not exist")
        self.approvals.validate(publication, snapshot)
        account = self.accounts.get(publication.account_id)
        if not account or not account.enabled: raise ValidationError("platform is disabled")
        if not self.credentials.is_available(account.credential_reference): raise ValidationError("credentials unavailable")
        for asset_id in snapshot.media_ids:
            asset = self.media.get(asset_id)
            if not asset or not asset.approved or asset.content_id != snapshot.content_id or asset.version != snapshot.version:
                raise ValidationError("media integrity validation failed")
        adapter = self.adapters.get(publication.platform)
        if not adapter or not adapter.health_check(): raise ValidationError("platform adapter unavailable")
        adapter.validate(publication, snapshot)
        return snapshot, adapter

    def process(self, publication_id: str):
        publication = self.repo.get(publication_id)
        if not publication: raise ValidationError("publication does not exist")
        lock = self._locks.setdefault(publication_id, Lock())
        if not lock.acquire(blocking=False): raise ValidationError("publication is already being processed")
        try:
            existing = self.idempotency.receipt(publication.idempotency_key)
            if existing: return existing
            if not self.idempotency.claim(publication.idempotency_key, publication_id):
                raise ValidationError("idempotency key already claimed")
            snapshot, adapter = self.preflight(publication)
            publication.status = PublicationStatus.PUBLISHING; self._record(publication, "PublicationStarted")
            result = adapter.publish(adapter.prepare(publication, snapshot), publication.idempotency_key)
            publication.status, publication.published_at = PublicationStatus.PUBLISHED, self.clock.now()
            publication.external_publication_id = result.external_id
            receipt = PublicationReceipt(publication_id, publication.platform, result.external_id,
                publication.published_at, publication.content_version, publication.account_id,
                result.checksum, result.metadata, result.public_url)
            self.idempotency.complete(publication.idempotency_key, receipt)
            self._record(publication, "PublicationSucceeded", external_id=result.external_id)
            self.events.publish("PublicationReceiptCreated", {"publication_id": publication_id})
            self.repo.save(publication); return receipt
        except PublishingError as error:
            publication.retry_count += 1; publication.error_state = error.category
            if self.retry_policy.eligible(error.category, publication.retry_count):
                publication.status = PublicationStatus.RETRYING
                self._record(publication, "PublicationRetried", retry_number=publication.retry_count)
                self.queue.enqueue(publication_id, self.clock.now() + self.retry_policy.backoff(publication.retry_count))
            else:
                publication.status = PublicationStatus.FAILED
                self._record(publication, "PublicationFailed", category=error.category.value, incident=True)
            self.repo.save(publication); raise
        finally: lock.release()

    def cancel(self, publication_id):
        publication = self.repo.get(publication_id)
        if publication.status == PublicationStatus.PUBLISHED: raise ValidationError("published history is immutable")
        publication.status = PublicationStatus.CANCELLED; self.queue.cancel(publication_id)
        self._record(publication, "PublicationCancelled"); self.repo.save(publication)

    def set_global_pause(self, enabled: bool, actor: str):
        self.global_pause = enabled
        if enabled:
            self.queue.pause()
        else:
            self.queue.resume()
        event = AuditEvent("EmergencyPauseEnabled" if enabled else "EmergencyPauseDisabled", "GLOBAL", self.clock.now(), {"actor": actor})
        self.audit.append(event); self.events.publish(event.event_type, event.details)

    def delete_external(self, publication_id, *, founder_approval_id=None):
        if not founder_approval_id: raise ValidationError("external deletion requires Founder approval")
        raise UnsupportedOperation("external deletion adapters are not enabled in Sprint 011")
