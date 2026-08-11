"""Guardian, security, budget, transcript and founder authority services."""
from dataclasses import dataclass
from .models import FounderFeedback, VideoAsset, VideoIdentityLock, VideoStatus
from .evaluation import TemporalIdentityResult, LipSyncResult, MotionResult

class SecurityError(PermissionError): pass

@dataclass
class BudgetLedger:
    per_video: float; daily: float; monthly: float; spent_daily: float=0; spent_monthly: float=0
    def authorize(self, amount: float) -> VideoStatus | None:
        if amount < 0: raise ValueError("cost cannot be negative")
        if amount > self.per_video or self.spent_daily+amount > self.daily or self.spent_monthly+amount > self.monthly:
            return VideoStatus.WAITING_FOUNDER_APPROVAL
        self.spent_daily += amount; self.spent_monthly += amount; return None

def authorize_reference_upload(provider_approved: bool, founder_approved: bool) -> None:
    if not (provider_approved and founder_approved): raise SecurityError("DENIED: canonical reference upload is not approved")

def transcript_matches(approved: str, generated: str) -> bool:
    normalize=lambda value: " ".join(value.casefold().split())
    return normalize(approved) == normalize(generated)

class VideoGuardian:
    def review(self, asset: VideoAsset, lock: VideoIdentityLock, temporal: TemporalIdentityResult,
               lipsync: LipSyncResult, motion: MotionResult, transcript_ok: bool, voice_identity_ok: bool) -> VideoStatus:
        if asset.identity_score < lock.minimum_identity_score or not temporal.passed: return VideoStatus.REJECTED_IDENTITY
        if not voice_identity_ok: return VideoStatus.REJECTED_VOICE_IDENTITY
        if not transcript_ok or not lipsync.passed or asset.lipsync_score < lock.minimum_lipsync_score: return VideoStatus.REJECTED_LIPSYNC
        if not motion.passed: return VideoStatus.REJECTED_MOTION
        return VideoStatus.FOUNDER_REVIEW

def apply_founder_feedback(asset: VideoAsset, feedback: FounderFeedback) -> VideoStatus:
    if feedback.accepted: return VideoStatus.APPROVED
    if feedback.category in {"TOO_ROBOTIC","TOO_ACTIVE","TOO_STATIC","BAD_GESTURE","BAD_EYE_CONTACT","BAD_POSTURE","UNNATURAL_BLINK","UNNATURAL_WALK"}:
        return VideoStatus.REJECTED_MOTION_IDENTITY
    return VideoStatus.REJECTED_QUALITY

def can_publish(asset: VideoAsset) -> bool:
    return asset.status == VideoStatus.APPROVED and asset.guardian_status == "APPROVED" and asset.founder_status == "APPROVED"
