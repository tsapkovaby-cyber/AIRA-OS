from dataclasses import dataclass

from .visual.domain import VisualIdentityProfile


@dataclass(frozen=True)
class DigitalHumanProfile:
    """Modalities expressing one underlying character; voice/motion are future work."""

    character_id: str
    core_identity_id: str
    behavior_profile_id: str
    visual_identity: VisualIdentityProfile
    voice_profile_id: str | None = None
    motion_profile_id: str | None = None
