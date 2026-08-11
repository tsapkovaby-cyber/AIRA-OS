from dataclasses import dataclass

from .voice.domain import VoiceIdentityProfile


@dataclass(frozen=True)
class DigitalHumanProfile:
    """Binds AIRA's independently versioned expression layers."""

    profile_id: str
    visual_identity_id: str
    voice_identity: VoiceIdentityProfile
    behavior_profile_id: str
    core_identity_id: str = "AIRA_CORE_IDENTITY"

    def __post_init__(self) -> None:
        if self.voice_identity.character_id != "AIRA":
            raise ValueError("Digital human voice must belong to AIRA")
