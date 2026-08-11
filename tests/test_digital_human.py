from dataclasses import replace
import pytest
from backend.digital_human.catalog import *
from backend.digital_human.engine import *
from backend.digital_human.models import *
from backend.digital_human.providers import *


class Provider:
    name = "controlled-test-provider"
    def __init__(self, cost=2, capabilities=None): self.cost, self.capabilities = cost, capabilities or {"PHOTOREALISM", "IDENTITY_REFERENCE"}
    def generate_image(self, request, prompt): return []
    def edit_image(self, asset_id, instructions): return {}
    def generate_variations(self, asset_id, count): return []
    def get_capabilities(self): return self.capabilities
    def estimate_cost(self, request): return self.cost
    def health_check(self): return True


def request(**changes):
    base = dict(request_id="r1", character_id="AIRA", identity_version="1.0", purpose="post", platform="Instagram Feed", scene="workspace", wardrobe=WardrobeSpec("white shirt", "white"), pose="working", expression=Expression.FOCUSED, camera=CameraSpec("medium portrait"), lighting="window", aspect_ratio="4:5", reference_ids=(MASTER_REFERENCE.asset_id,), task_profile="aira_lifestyle", provider_policy="approved-only", candidate_count=4, cost_limit=10)
    base.update(changes); return VisualGenerationRequest(**base)


def asset(**changes):
    base = dict(asset_id="a1", character_id="AIRA", identity_version="1.0", generation_request_id="r1", provider="test", model="test", prompt_version="v1", reference_ids=(MASTER_REFERENCE.asset_id,), scene="workspace", wardrobe=WardrobeSpec("shirt", "white"), pose="working", expression=Expression.FOCUSED, camera=CameraSpec("portrait"), lighting="window", file_reference="asset://generated/a1", sha256="hash")
    base.update(changes); return VisualAsset(**base)


def test_identity_pack_and_reference_hierarchy_validation():
    assert AIRA_VISUAL_IDENTITY_PACK_V1.eye_profile.color == "blue"
    assert MASTER_REFERENCE.level.value < ReferenceLevel.GENERATED_CONTENT.value
    with pytest.raises(ValueError): replace(MASTER_REFERENCE, founder_approved=False)


def test_only_one_active_identity_and_master_protection():
    registry = IdentityRegistry(); registry.save(AIRA_VISUAL_IDENTITY_PACK_V1)
    with pytest.raises(ValueError): registry.save(replace(AIRA_VISUAL_IDENTITY_PACK_V1, identity_id="v2"))
    library = AssetLibrary(); library.register_reference(MASTER_REFERENCE)
    with pytest.raises(PermissionError): library.register_reference(replace(MASTER_REFERENCE, sha256="other"))


def test_generation_validation_and_cost_limit():
    with pytest.raises(ValueError): request(aspect_ratio="3:2")
    router = VisualModelRouter([ProviderProfile(Provider(20), True, "high", "none", "none", "ok", "EU")])
    with pytest.raises(PermissionError, match="WAITING_FOUNDER_APPROVAL"): router.route({"IDENTITY_REFERENCE"}, request())


def test_router_ignores_unapproved_provider_and_is_provider_independent():
    bad, good = Provider(1), Provider(2)
    router = VisualModelRouter([ProviderProfile(bad, False, "", "", "", "", ""), ProviderProfile(good, True, "", "", "", "", "")])
    assert router.route({"PHOTOREALISM"}, request()) is good


def test_prompt_layers_are_ordered_and_complete():
    registry = PromptRegistry({})
    layers = {key: key for key in reversed(PROMPT_ORDER)}
    prompt = registry.build(layers)
    assert prompt.splitlines()[0].startswith("[IDENTITY]")
    with pytest.raises(ValueError): registry.build({"identity": "AIRA"})


def test_lineage_and_founder_only_promotion():
    library = AssetLibrary(); parent = asset(); parent.status = AssetStatus.APPROVED; library.add(parent)
    child = asset(asset_id="a2", parent_asset_id="a1"); library.add(child)
    with pytest.raises(PermissionError): library.promote("a1", founder_authorized=False)
    assert library.promote("a1", founder_authorized=True).level is ReferenceLevel.FOUNDER_APPROVED_REFERENCE
    with pytest.raises(ValueError): library.add(asset(asset_id="orphan", parent_asset_id="missing"))


class Score:
    def __init__(self, score): self.score = score
    def evaluate(self, *args): return self.score
class Guardian:
    def review(self, asset): return True, ()


def test_beautiful_but_wrong_is_rejected_and_founder_override_is_final():
    memory = FeedbackMemory(); engine = DigitalHumanEngine(None, None, AssetLibrary(), memory)
    candidate = engine.evaluate(asset(), AIRA_VISUAL_IDENTITY_PACK_V1, Score(68), Score(97), Guardian())
    assert candidate.status is AssetStatus.REJECTED_IDENTITY
    accepted_by_machine = engine.evaluate(asset(asset_id="a2"), AIRA_VISUAL_IDENTITY_PACK_V1, Score(93), Score(95), Guardian())
    engine.founder_decision(accepted_by_machine, False, "eyes too large", "FACE_GEOMETRY")
    assert accepted_by_machine.status is AssetStatus.REJECTED_IDENTITY
    assert memory.entries[-1].reason == "eyes too large"


def test_incorrect_eyes_and_hair_reduce_score_via_composite_evaluator_contract():
    class FeatureEvaluator:
        def evaluate(self, candidate, identity):
            flags = candidate.usage_rights_metadata.get("drift", ())
            return 95 - 20 * len(flags)
    engine = DigitalHumanEngine(None, None, AssetLibrary(), FeedbackMemory())
    wrong = asset(usage_rights_metadata={"drift": ("brown eyes", "dark hair", "different face")})
    assert engine.evaluate(wrong, AIRA_VISUAL_IDENTITY_PACK_V1, FeatureEvaluator(), Score(99), Guardian()).status is AssetStatus.REJECTED_IDENTITY


def test_provider_receives_only_generation_contract_not_private_context():
    req = request()
    assert not hasattr(req, "founder_private_data")
    assert set(req.reference_ids) == {"AIRA_MASTER_REFERENCE_V1"}
