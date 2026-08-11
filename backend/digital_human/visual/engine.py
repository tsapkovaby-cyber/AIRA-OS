from dataclasses import replace

from .domain import AssetStatus, IdentityLock, MediaDisclosure, VisualAsset, VisualGenerationRequest, VisualIdentityProfile
from .evaluation import IdentityEvaluator, VisualGuardian
from .prompts import VisualPromptBuilder
from .providers import VisualModelRouter
from .repository import AssetRepository


class BudgetApprovalRequired(RuntimeError):
    pass


class DigitalHumanEngine:
    def __init__(self, router: VisualModelRouter, evaluator: IdentityEvaluator, guardian: VisualGuardian,
                 assets: AssetRepository, prompt_builder: VisualPromptBuilder | None = None,
                 daily_budget: float = 100, monthly_budget: float = 1000) -> None:
        self.router, self.evaluator, self.guardian, self.assets = router, evaluator, guardian, assets
        self.prompt_builder = prompt_builder or VisualPromptBuilder()
        self.daily_budget, self.monthly_budget = daily_budget, monthly_budget
        self.daily_spend = self.monthly_spend = 0.0

    def generate(self, request: VisualGenerationRequest, identity: VisualIdentityProfile,
                 identity_lock: IdentityLock) -> list[VisualAsset]:
        if set(identity_lock.canonical_reference_ids) - set(request.reference_ids):
            raise ValueError("request omitted canonical identity references")
        provider = self.router.route(request)
        cost = provider.estimate_cost(request)
        if self.daily_spend + cost > self.daily_budget or self.monthly_spend + cost > self.monthly_budget:
            raise BudgetApprovalRequired("WAITING_FOUNDER_APPROVAL")
        prompt = self.prompt_builder.build(identity, identity_lock, request)
        outputs = provider.generate_image(request, prompt)
        self.daily_spend += cost
        self.monthly_spend += cost
        results = []
        for output in outputs:
            asset = VisualAsset(
                asset_id=output.provider_generation_id, character_id=request.character_id,
                identity_version=request.identity_version, generation_request_id=request.request_id,
                provider=provider.provider_id, model=output.model, prompt_version="visual.layered.v1",
                reference_ids=request.reference_ids, scene=request.scene, wardrobe=request.wardrobe,
                pose=request.pose, expression=request.expression, camera=request.camera, lighting=request.lighting,
                file_reference=output.file_reference, sha256=output.sha256,
                disclosure=MediaDisclosure(provider=provider.provider_id, model=output.model),
                status=AssetStatus.EVALUATING)
            evaluation = self.evaluator.evaluate(asset)
            passed, _ = self.guardian.review(asset, evaluation)
            if evaluation.identity_score < 70:
                status = AssetStatus.REJECTED_IDENTITY
            elif evaluation.quality_score < 80:
                status = AssetStatus.REJECTED_QUALITY
            elif passed:
                status = AssetStatus.FOUNDER_REVIEW if request.founder_approval_required else AssetStatus.APPROVED
            else:
                status = AssetStatus.GUARDIAN_REVIEW
            asset = replace(asset, identity_score=evaluation.identity_score, quality_score=evaluation.quality_score,
                            guardian_status="PASS" if passed else "REVIEW", status=status)
            self.assets.save(asset)
            results.append(asset)
        return results

    def founder_decision(self, asset: VisualAsset, *, approved: bool) -> VisualAsset:
        status = AssetStatus.APPROVED if approved else AssetStatus.REJECTED_IDENTITY
        decided = replace(asset, founder_status="APPROVED" if approved else "REJECTED", status=status,
                          disclosure=replace(asset.disclosure, human_reviewed=True, founder_approved=approved))
        self.assets.save(decided)
        return decided
