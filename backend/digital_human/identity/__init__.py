"""Canonical identity bootstrap."""

from backend.digital_human.visual.domain import (
    AssetReference, FaceProfile, IdentityStatus, ReferenceLevel, VisualIdentityProfile,
)

MASTER_REFERENCE_ID = "AIRA_MASTER_REFERENCE_V1"


def register_master_reference(file_reference: str, sha256: str) -> AssetReference:
    """Register metadata only: image binaries remain in protected Asset Storage."""
    return AssetReference(MASTER_REFERENCE_ID, file_reference, sha256, ReferenceLevel.MASTER_REFERENCE,
                          founder_approved=True, read_only=True)


def aira_visual_identity_pack_v1(master: AssetReference) -> VisualIdentityProfile:
    if master.asset_id != MASTER_REFERENCE_ID or master.level is not ReferenceLevel.MASTER_REFERENCE:
        raise ValueError("the Founder-approved master reference is required")
    return VisualIdentityProfile(
        identity_id="AIRA_VISUAL_IDENTITY_PACK_V1", character_id="AIRA", name="AIRA", version="1.0",
        status=IdentityStatus.ACTIVE, founder_approved=True, master_reference_id=master.asset_id,
        reference_ids=(master.asset_id,),
        face=FaceProfile(
            visible_attributes=("young adult woman", "photorealistic feminine natural face", "balanced defined brows", "expressive lashes"),
            reference_ids=(master.asset_id,),
        ),
        history=("Founder-approved Sprint 018 registration; reference remains authoritative",),
    )
