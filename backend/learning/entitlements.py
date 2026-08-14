"""Plan and entitlement foundation for AIRA Academy.

This module intentionally contains no payment-provider integration. It models
access independently so Stripe/local processors can be connected later without
coupling billing to the learning domain.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum

class PlanCode(str, Enum):
    FREE = "free"
    BASIC = "basic"
    ADVANCED = "advanced"
    PREMIUM = "premium"
    OWNER = "owner"

@dataclass(frozen=True, slots=True)
class Plan:
    code: PlanCode
    title: str
    entitlements: frozenset[str]
    hidden: bool = False

CATALOG: dict[PlanCode, Plan] = {
    PlanCode.FREE: Plan(PlanCode.FREE, "Free", frozenset({"placement", "course_preview", "limited_text_tutor"})),
    PlanCode.BASIC: Plan(PlanCode.BASIC, "Basic", frozenset({"placement", "courses", "progress", "text_tutor"})),
    PlanCode.ADVANCED: Plan(PlanCode.ADVANCED, "Advanced", frozenset({"placement", "courses", "progress", "text_tutor", "voice_tutor", "video_lessons"})),
    PlanCode.PREMIUM: Plan(PlanCode.PREMIUM, "Premium", frozenset({"placement", "courses", "progress", "text_tutor", "voice_tutor", "video_lessons", "personalized_path", "priority_features"})),
    PlanCode.OWNER: Plan(PlanCode.OWNER, "Owner / Developer", frozenset({"*"}), hidden=True),
}

@dataclass(slots=True)
class StudentEntitlement:
    student_id: str
    plan: PlanCode = PlanCode.FREE
    overrides: set[str] = field(default_factory=set)

class EntitlementService:
    def __init__(self) -> None:
        self._accounts: dict[str, StudentEntitlement] = {}

    def assign_plan(self, student_id: str, plan: PlanCode | str) -> StudentEntitlement:
        plan_code = PlanCode(plan)
        account = self._accounts.setdefault(student_id, StudentEntitlement(student_id))
        account.plan = plan_code
        return account

    def grant(self, student_id: str, entitlement: str) -> None:
        account = self._accounts.setdefault(student_id, StudentEntitlement(student_id))
        account.overrides.add(entitlement)

    def has_access(self, student_id: str, entitlement: str) -> bool:
        account = self._accounts.get(student_id, StudentEntitlement(student_id))
        plan = CATALOG[account.plan]
        return "*" in plan.entitlements or entitlement in plan.entitlements or entitlement in account.overrides

    def visible_plans(self) -> list[Plan]:
        return [plan for plan in CATALOG.values() if not plan.hidden]
