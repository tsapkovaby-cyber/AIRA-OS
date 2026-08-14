"""In-memory ports suitable for tests; persistent adapters can implement the same API."""

from dataclasses import replace

from .domain import AssetReference, IdentityStatus, ReferenceLevel, VisualAsset, VisualFeedback, VisualIdentityProfile


class ProtectionError(PermissionError):
    pass


class IdentityRepository:
    def __init__(self) -> None:
        self.items: dict[str, VisualIdentityProfile] = {}

    def save(self, profile: VisualIdentityProfile) -> None:
        if profile.status is IdentityStatus.ACTIVE:
            active = [p for p in self.items.values() if p.status is IdentityStatus.ACTIVE and p.identity_id != profile.identity_id]
            if active:
                raise ValueError("only one canonical ACTIVE identity is allowed")
        self.items[profile.identity_id] = profile


class ReferenceRepository:
    def __init__(self) -> None:
        self.items: dict[str, AssetReference] = {}

    def register(self, reference: AssetReference) -> None:
        if reference.asset_id in self.items:
            raise ProtectionError("references are immutable; create a new version")
        self.items[reference.asset_id] = reference

    def delete(self, asset_id: str, *, founder_workflow_approved: bool = False) -> None:
        ref = self.items[asset_id]
        if ref.level is ReferenceLevel.MASTER_REFERENCE or ref.read_only:
            raise ProtectionError("master/read-only references cannot be deleted")
        if not founder_workflow_approved:
            raise ProtectionError("Founder workflow required")
        del self.items[asset_id]

    def promote(self, asset_id: str, *, founder_id: str | None) -> AssetReference:
        source = self.items[asset_id]
        if not founder_id:
            raise ProtectionError("only Founder may promote a reference")
        promoted = replace(source, asset_id=f"{asset_id}:founder-reference", level=ReferenceLevel.FOUNDER_APPROVED_REFERENCE,
                           founder_approved=True, read_only=True)
        self.register(promoted)
        return promoted


class AssetRepository:
    def __init__(self) -> None:
        self.items: dict[str, VisualAsset] = {}

    def save(self, asset: VisualAsset) -> None:
        if asset.parent_asset_id and asset.parent_asset_id not in self.items:
            raise ValueError("lineage parent does not exist")
        self.items[asset.asset_id] = asset


class FeedbackRepository:
    def __init__(self) -> None:
        self.items: list[VisualFeedback] = []

    def record(self, feedback: VisualFeedback) -> None:
        if not feedback.founder_id or not feedback.reason.strip():
            raise ValueError("Founder and reason are required")
        self.items.append(feedback)
