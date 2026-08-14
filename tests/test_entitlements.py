from backend.learning.entitlements import EntitlementService, PlanCode


def test_free_plan_has_only_entry_access():
    access = EntitlementService()
    assert access.has_access("s1", "placement")
    assert not access.has_access("s1", "voice_tutor")


def test_advanced_unlocks_voice_and_video():
    access = EntitlementService()
    access.assign_plan("s1", PlanCode.ADVANCED)
    assert access.has_access("s1", "voice_tutor")
    assert access.has_access("s1", "video_lessons")


def test_owner_plan_is_hidden_and_has_all_access():
    access = EntitlementService()
    access.assign_plan("founder", PlanCode.OWNER)
    assert access.has_access("founder", "future_feature")
    assert PlanCode.OWNER not in {plan.code for plan in access.visible_plans()}


def test_explicit_override_can_grant_feature_without_changing_plan():
    access = EntitlementService()
    access.grant("s1", "beta_feature")
    assert access.has_access("s1", "beta_feature")
    assert not access.has_access("s1", "voice_tutor")
