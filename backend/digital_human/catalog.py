"""Canonical Sprint 018 identity pack and benchmark declarations."""
from .models import *

MASTER_REFERENCE = AssetReference(
    "AIRA_MASTER_REFERENCE_V1", "asset://canonical/aira/master/v1", "founder-supplied-asset-hash-managed-by-storage", ReferenceLevel.MASTER_REFERENCE, True, True
)

AIRA_VISUAL_IDENTITY_PACK_V1 = VisualIdentityProfile(
    identity_id="AIRA_VISUAL_IDENTITY_PACK_V1", character_id="AIRA", name="AIRA", version="1.0",
    status=IdentityStatus.ACTIVE, founder_approved=True, master_reference=MASTER_REFERENCE,
    reference_set=[MASTER_REFERENCE],
    face_profile=FaceProfile((MASTER_REFERENCE.asset_id,), ("feminine", "natural", "consistent facial geometry", "balanced defined brows", "expressive eyelashes")),
)

IDENTITY_LOCK_V1 = IdentityLock((MASTER_REFERENCE.asset_id,), ("preserve facial geometry", "preserve nose/lip proportions", "preserve jawline and face width"))

AIRA_VISUAL_IDENTITY_V1 = (
    "01_REFERENCE_REPRODUCTION", "02_SOFT_SMILE", "03_30_DEGREE_LEFT", "04_30_DEGREE_RIGHT",
    "05_WHITE_SHIRT_WORKSPACE", "06_NATURAL_DAYLIGHT", "07_PURPLE_ACCENT_LIGHT", "08_OUTDOOR_LIFESTYLE",
)

PROMPT_COMPONENTS_V1 = {
    "visual.identity.v1": "stable AIRA identity anchored exclusively by supplied canonical references",
    "visual.skin.v1": "natural light skin texture; realistic highlights and shadows; minimal retouching",
    "visual.hair.v1": "long light-blonde natural soft voluminous hair",
    "visual.brand.v1": "modern clean premium natural approachable minimal photography",
    "visual.camera.lifestyle.v1": "believable lifestyle photography with natural framing",
    "visual.camera.editorial.v1": "clean contemporary editorial photography",
    "visual.quality.photoreal.v1": "photorealistic anatomy and materials",
    "visual.negative.v1": "do not change identity or eye color; no plastic skin, fantasy styling, random text, or unspecified accessories",
}
