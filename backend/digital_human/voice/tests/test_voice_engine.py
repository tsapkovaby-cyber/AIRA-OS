from dataclasses import replace

import pytest

from backend.digital_human.voice.catalog import CANONICAL_PROFILE, INITIAL_LEXICON, MASTER_REFERENCE
from backend.digital_human.voice.domain import (
    Budget, Emotion, Pace, ProviderStatus, ProviderVoiceProfile, ReferenceLevel,
    SpeechAsset, SpeechAssetStatus, SpeechGenerationRequest, VoiceFeedback, VoiceIdentityLock,
)
from backend.digital_human.voice.providers import ProviderCapabilities, RoutingCandidate, SpeechProvider, SynthesisResult, VoiceRouter
from backend.digital_human.voice.service import Guardian, SpeechEngine, VoiceEvaluator


class FakeProvider(SpeechProvider):
    name = "fake"

    def __init__(self, spoken_text=None, cost=1): self.spoken_text, self.cost = spoken_text, cost
    def synthesize(self, request, profile): return SynthesisResult(b"audio", self.spoken_text or request.text, self.cost)
    def get_capabilities(self): return ProviderCapabilities(("ru", "en"), True, True, True, False)
    def estimate_cost(self, request): return self.cost
    def health_check(self): return True


def request(**changes):
    base = SpeechGenerationRequest("1", "AIRA", "V1", "Сегодня тест.", "ru", "aira_voice_telegram", Emotion.AIRA_DEFAULT, Pace.NORMAL, "reply", "telegram", cost_limit=2)
    return replace(base, **changes)


def candidate(status=ProviderStatus.APPROVED, provider=None, similarity=95):
    provider = provider or FakeProvider()
    profile = ProviderVoiceProfile("pp1", "fake", "external", "V1", status, "AIRA_ONLY", True)
    return RoutingCandidate(provider, profile, similarity, 90, 80, 80, 10, 90, 85, 90)


def asset(status=SpeechAssetStatus.GENERATED):
    return SpeechAsset("a", "AIRA", "V1", "r", "p", "pp1", "tv", "ru", Emotion.NEUTRAL, Pace.NORMAL, "V1", None, None, "PENDING", "APPROVED", "x.wav", "hash", "pp1", status)


def test_canonical_profile_and_consent_are_protected():
    assert CANONICAL_PROFILE.status == "ACTIVE"
    assert CANONICAL_PROFILE.consent.automatic_third_party_sharing is False
    assert MASTER_REFERENCE.level is ReferenceLevel.MASTER and MASTER_REFERENCE.read_only
    with pytest.raises(PermissionError): CANONICAL_PROFILE.replace_master(MASTER_REFERENCE)
    with pytest.raises(ValueError): replace(CANONICAL_PROFILE, master_reference=replace(MASTER_REFERENCE, read_only=False))


def test_reference_hierarchy_never_promotes_generated_audio():
    generated = replace(MASTER_REFERENCE, level=ReferenceLevel.GENERATED)
    with pytest.raises(ValueError): generated.derive("x", "x.wav", "hash")
    assert MASTER_REFERENCE.derive("clean", "clean.wav", "hash").parent_asset_id == MASTER_REFERENCE.asset_id


def test_request_pronunciation_and_high_risk_validation():
    assert {x.term for x in INITIAL_LEXICON} >= {"AIRA", "OpenAI", "LLM"}
    assert all(x.pronunciation_hint == "FOUNDER_REVIEW_REQUIRED" for x in INITIAL_LEXICON if x.term == "AIRA")
    with pytest.raises(ValueError): request(text="")
    with pytest.raises(ValueError): request(high_risk=True)


def test_router_denies_unapproved_provider_and_prefers_identity():
    with pytest.raises(PermissionError): VoiceRouter().route(request(), [candidate(ProviderStatus.RESEARCHED)])
    assert VoiceRouter().route(request(), [candidate(similarity=90), candidate(similarity=96)]).voice_similarity == 96


def test_lineage_budget_and_text_integrity():
    with pytest.raises(ValueError): replace(asset(), parent_asset_id="")
    engine = SpeechEngine(VoiceRouter(), Guardian(), Budget(2, 5, 20, 3))
    assert engine.generate(request(), [candidate()]).guardian_status == "APPROVED"
    with pytest.raises(PermissionError, match="WAITING_FOUNDER_APPROVAL"):
        engine.generate(request(), [candidate(provider=FakeProvider(cost=3))])
    altered = engine.generate(request(), [candidate(provider=FakeProvider("Изменено."))])
    assert altered.guardian_status == "REJECTED_TEXT_INTEGRITY"


def test_identity_has_priority_and_founder_can_override():
    evaluator = VoiceEvaluator()
    lock = VoiceIdentityLock(MASTER_REFERENCE.asset_id, (MASTER_REFERENCE.asset_id,), "V1")
    assert evaluator.evaluate(asset(), 69, 99, lock).status is SpeechAssetStatus.REJECTED_IDENTITY
    assert evaluator.evaluate(asset(), 75, 99, lock).status is SpeechAssetStatus.FOUNDER_REVIEW
    feedback = VoiceFeedback("a", "IDENTITY", "HIGH", "p", "telegram", "REJECTED", "Это не голос AIRA.")
    assert evaluator.founder_override(evaluator.evaluate(asset(), 94, 99, lock), feedback).status is SpeechAssetStatus.REJECTED_IDENTITY
