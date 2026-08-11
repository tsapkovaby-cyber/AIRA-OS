from __future__ import annotations

import hashlib

from .domain import Budget, SpeechAsset, SpeechAssetStatus, SpeechGenerationRequest, VoiceFeedback, VoiceIdentityLock
from .providers import RoutingCandidate, VoiceRouter


class Guardian:
    def review(self, request: SpeechGenerationRequest, spoken_text: str) -> str:
        if spoken_text.strip() != request.text.strip():
            return "REJECTED_TEXT_INTEGRITY"
        return "APPROVED"


class VoiceEvaluator:
    def evaluate(self, asset: SpeechAsset, identity_score: float, quality_score: float, lock: VoiceIdentityLock) -> SpeechAsset:
        status = lock.decision(identity_score)
        if status is SpeechAssetStatus.APPROVED and quality_score < 70:
            status = SpeechAssetStatus.REJECTED_QUALITY
        return asset.with_status(status)

    def founder_override(self, asset: SpeechAsset, feedback: VoiceFeedback) -> SpeechAsset:
        if feedback.result == "REJECTED":
            return asset.with_status(SpeechAssetStatus.REJECTED_IDENTITY)
        return asset


class SpeechEngine:
    def __init__(self, router: VoiceRouter, guardian: Guardian, budget: Budget) -> None:
        self.router, self.guardian, self.budget = router, guardian, budget

    def generate(self, request: SpeechGenerationRequest, candidates: list[RoutingCandidate], *, spent_today: float = 0, spent_month: float = 0) -> SpeechAsset:
        candidate = self.router.route(request, candidates)
        estimate = candidate.provider.estimate_cost(request)
        if estimate > request.cost_limit or not self.budget.authorize(estimate, spent_today, spent_month, request.speech_profile == "aira_voice_experiment"):
            raise PermissionError("WAITING_FOUNDER_APPROVAL: voice budget exceeded")
        result = candidate.provider.synthesize(request, candidate.profile)
        guardian_status = self.guardian.review(request, result.spoken_text)
        audio_hash = hashlib.sha256(result.audio).hexdigest()
        status = SpeechAssetStatus.GENERATED if guardian_status == "APPROVED" else SpeechAssetStatus.REJECTED_QUALITY
        return SpeechAsset(
            asset_id=f"SPEECH_{request.request_id}", character_id="AIRA", voice_identity_version=request.voice_identity_version,
            speech_request_id=request.request_id, provider=candidate.profile.provider,
            provider_voice_profile_id=candidate.profile.profile_id, text_version=hashlib.sha256(request.text.encode()).hexdigest(),
            language=request.language, emotion=request.emotion, pace=request.pace, pronunciation_version="V1",
            identity_score=None, quality_score=None, founder_status="PENDING", guardian_status=guardian_status,
            file_reference=f"generated/{request.request_id}.{request.output_format}", sha256=audio_hash,
            parent_asset_id=candidate.profile.profile_id, status=status,
        )
