"""Application services enforcing identity, approval, lineage, and budget rules."""

from __future__ import annotations
from dataclasses import replace
from typing import Protocol
from .models import *
from .providers import VisualModelRouter


PROMPT_ORDER = ("identity", "scene", "wardrobe", "pose", "expression", "camera", "lighting", "brand", "quality", "negative")


class PromptRegistry:
    def __init__(self, components: dict[str, str]): self.components = components
    def build(self, layers: dict[str, str]) -> str:
        missing = set(PROMPT_ORDER) - layers.keys()
        if missing: raise ValueError(f"missing prompt layers: {sorted(missing)}")
        return "\n".join(f"[{name.upper()}] {layers[name]}" for name in PROMPT_ORDER)


class IdentityEvaluator(Protocol):
    def evaluate(self, asset: VisualAsset, identity: VisualIdentityProfile) -> float: ...


class QualityEvaluator(Protocol):
    def evaluate(self, asset: VisualAsset) -> float: ...


class VisualGuardian(Protocol):
    def review(self, asset: VisualAsset) -> tuple[bool, tuple[str, ...]]: ...


class IdentityRegistry:
    def __init__(self): self.identities: dict[str, VisualIdentityProfile] = {}
    def save(self, profile: VisualIdentityProfile) -> None:
        if profile.status is IdentityStatus.ACTIVE:
            active = [p for p in self.identities.values() if p.character_id == profile.character_id and p.status is IdentityStatus.ACTIVE and p.identity_id != profile.identity_id]
            if active: raise ValueError("only one ACTIVE identity is allowed")
        existing = self.identities.get(profile.identity_id)
        if existing and existing.master_reference != profile.master_reference:
            raise PermissionError("DENIED: master replacement requires explicit Founder workflow")
        self.identities[profile.identity_id] = profile


class AssetLibrary:
    def __init__(self):
        self.assets: dict[str, VisualAsset] = {}
        self.references: dict[str, AssetReference] = {}

    def register_reference(self, reference: AssetReference) -> None:
        old = self.references.get(reference.asset_id)
        if old and old.level is ReferenceLevel.MASTER_REFERENCE and old != reference:
            raise PermissionError("DENIED: master references cannot be overwritten")
        self.references[reference.asset_id] = reference

    def add(self, asset: VisualAsset) -> None:
        if asset.parent_asset_id and asset.parent_asset_id not in self.assets:
            raise ValueError("lineage parent does not exist")
        self.assets[asset.asset_id] = asset

    def promote(self, asset_id: str, *, founder_authorized: bool) -> AssetReference:
        if not founder_authorized: raise PermissionError("only Founder may promote references")
        asset = self.assets[asset_id]
        if asset.status is not AssetStatus.APPROVED: raise ValueError("only approved assets may be promoted")
        ref = AssetReference(asset.asset_id, asset.file_reference, asset.sha256, ReferenceLevel.FOUNDER_APPROVED_REFERENCE, True, True, asset.parent_asset_id)
        self.register_reference(ref)
        return ref


class FeedbackMemory:
    def __init__(self): self.entries: list[VisualFeedback] = []
    def record(self, feedback: VisualFeedback) -> None: self.entries.append(feedback)


class DigitalHumanEngine:
    def __init__(self, router: VisualModelRouter, prompts: PromptRegistry, assets: AssetLibrary, feedback: FeedbackMemory):
        self.router, self.prompts, self.assets, self.feedback = router, prompts, assets, feedback

    def evaluate(self, asset: VisualAsset, identity: VisualIdentityProfile, identity_evaluator: IdentityEvaluator, quality_evaluator: QualityEvaluator, guardian: VisualGuardian) -> VisualAsset:
        asset.status = AssetStatus.EVALUATING
        asset.identity_score = identity_evaluator.evaluate(asset, identity)
        asset.quality_score = quality_evaluator.evaluate(asset)
        if asset.identity_score < 70:
            asset.status = AssetStatus.REJECTED_IDENTITY
            return asset
        if asset.quality_score < 80:
            asset.status = AssetStatus.REJECTED_QUALITY
            return asset
        passed, _ = guardian.review(asset)
        asset.guardian_status = "PASS" if passed else "REJECT"
        asset.status = AssetStatus.FOUNDER_REVIEW if passed else AssetStatus.GUARDIAN_REVIEW
        return asset

    def founder_decision(self, asset: VisualAsset, approved: bool, reason: str = "", category: str = "IDENTITY") -> None:
        asset.founder_status = "APPROVED" if approved else "REJECTED"
        asset.disclosure["human_reviewed"] = True
        asset.disclosure["founder_approved"] = approved
        asset.status = AssetStatus.APPROVED if approved else AssetStatus.REJECTED_IDENTITY
        if not approved:
            self.feedback.record(VisualFeedback(asset.asset_id, category, "HIGH", reason, "REJECTED"))
