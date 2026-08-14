from .domain import *


INITIAL_TERMS = ("AIRA", "AI", "OpenAI", "ChatGPT", "Codex", "LLM", "API", "Telegram", "Instagram", "TikTok", "YouTube", "RAG", "Agent", "Prompt", "Model", "Tool")

INITIAL_LEXICON = tuple(
    PronunciationEntry(term, language, term, "FOUNDER_REVIEW_REQUIRED" if term == "AIRA" else "TEST_REQUIRED")
    for term in INITIAL_TERMS for language in ("ru", "en")
)

MASTER_REFERENCE = VoiceReference(
    asset_id=MASTER_REFERENCE_ID, level=ReferenceLevel.MASTER,
    file_reference="protected://founder/AIRA_MASTER_VOICE_REFERENCE_V1",
    sha256="PENDING_SECURE_INGEST", founder_approved=True, read_only=True,
)

CANONICAL_PROFILE = VoiceIdentityProfile(
    voice_identity_id=VOICE_IDENTITY_ID, character_id="AIRA", version="V1", master_reference=MASTER_REFERENCE,
    approved_reference_ids=(MASTER_REFERENCE_ID,),
    voice_characteristics={"identity": "Founder-derived", "timbre": "stable", "texture": "natural"},
    speech_styles={"AIRA_DEFAULT": {"delivery": "calm, friendly, confident, slightly warm"}, "AIRA_TELEGRAM": {"delivery": "natural, warm, short, direct"}},
    language_profiles={"ru": {"priority": "primary", "pronunciation": "natural"}, "en": {"priority": "secondary", "accent": "not specified"}},
    pronunciation_rules=INITIAL_LEXICON, emotion_profiles=tuple(Emotion), pacing_rules=tuple(Pace), provider_profile_ids=(),
    safety_rules=("APPROVED_TEXT_ONLY", "NO_IMPERSONATION", "NO_UNAPPROVED_PROVIDER_UPLOAD", "HIGH_RISK_FOUNDER_REVIEW"),
    consent=ConsentMetadata(), founder_approved=True, status=VoiceIdentityStatus.ACTIVE,
    created_at=utcnow(), updated_at=utcnow(), history=("Registered by Sprint 019",),
)

VOICE_BENCHMARK_SCENARIOS = (
    "01_NEUTRAL_RUSSIAN", "02_FRIENDLY_RUSSIAN", "03_AI_TERMINOLOGY", "04_LONG_SENTENCE",
    "05_SHORT_FORM_HOOK", "06_TELEGRAM_RESPONSE", "07_NUMBERS_AND_PRICES", "08_ENGLISH_TOOL_NAMES",
    "09_LONG_FORM_STABILITY", "10_EMOTION_CONTROL",
)
