from backend.accounts.models import AccountRole, UserAccount
from backend.learning.entitlements import CATALOG, EntitlementService, PlanCode


def test_owner_is_explicit_account_role():
    account = UserAccount(role=AccountRole.OWNER)
    assert account.role is AccountRole.OWNER


def test_owner_plan_is_hidden_from_commercial_catalog():
    service = EntitlementService()
    assert PlanCode.OWNER not in {plan.code for plan in service.visible_plans()}
    assert CATALOG[PlanCode.OWNER].hidden is True


def test_owner_entitlement_has_full_access():
    service = EntitlementService()
    service.assign_plan("founder", PlanCode.OWNER)
    assert service.has_access("founder", "voice_tutor")
    assert service.has_access("founder", "video_lessons")
    assert service.has_access("founder", "future_feature_not_yet_in_catalog")
