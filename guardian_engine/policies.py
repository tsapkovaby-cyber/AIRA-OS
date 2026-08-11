"""Guardian policy architecture and validation helpers."""

from __future__ import annotations

from dataclasses import dataclass

from .models import ApprovalStatus, EvidenceRecord, RiskCategory, RiskLevel, ValidationIssue

FOUNDER_APPROVAL_DOMAINS = frozenset({"brand", "business", "legal", "public_statement", "constitution"})
CONSTITUTION_KEYWORDS = frozenset({"mission", "values", "ethics", "transparency", "safety", "evidence"})


@dataclass(frozen=True)
class GuardianPolicy:
    """Architecture-only policy bundle used by the Guardian pipeline."""

    require_evidence_for_publication: bool = True
    require_confidence_for_recommendations: bool = True
    disclose_conflicts: bool = True
    distinguish_claim_types: bool = True
    require_explainability: bool = True
    separate_marketing_from_research: bool = True


def validate_evidence(records: list[EvidenceRecord]) -> list[ValidationIssue]:
    """Validate evidence completeness without judging source truthfulness."""

    issues: list[ValidationIssue] = []
    if not records:
        issues.append(
            ValidationIssue(
                category="Evidence",
                message="Publication cannot proceed without evidence records.",
                severity=RiskLevel.HIGH,
                recommendation="Attach primary and secondary sources for important claims.",
            )
        )
        return issues

    for record in records:
        if not record.has_required_sources():
            issues.append(
                ValidationIssue(
                    category="Evidence",
                    message=f"Claim lacks required primary and secondary sources: {record.claim}",
                    severity=RiskLevel.HIGH,
                    recommendation="Provide both source types before publication.",
                )
            )
        if not 0 <= record.confidence <= 1:
            issues.append(
                ValidationIssue(
                    category="Evidence",
                    message=f"Claim confidence must be between 0 and 1: {record.claim}",
                    severity=RiskLevel.MEDIUM,
                    recommendation="Normalize confidence as a decimal value.",
                )
            )
    return issues


def requires_founder_approval(domains: set[str]) -> ApprovalStatus:
    """Return founder approval status based on governed domains."""

    normalized = {domain.strip().lower() for domain in domains}
    if normalized & FOUNDER_APPROVAL_DOMAINS:
        return ApprovalStatus.PENDING_FOUNDER
    return ApprovalStatus.NOT_REQUIRED


def check_constitution_alignment(principles: set[str]) -> list[ValidationIssue]:
    """Check whether workflow metadata references required constitutional areas."""

    normalized = {principle.strip().lower() for principle in principles}
    missing = CONSTITUTION_KEYWORDS - normalized
    if not missing:
        return []
    return [
        ValidationIssue(
            category="Constitution",
            message="Workflow has not documented all constitutional checks.",
            severity=RiskLevel.HIGH,
            recommendation=f"Document checks for: {', '.join(sorted(missing))}.",
        )
    ]


def classify_risk(categories: set[RiskCategory], has_publication: bool) -> RiskLevel:
    """Classify architectural risk from declared categories and publication scope."""

    high_risk = {RiskCategory.LEGAL, RiskCategory.SECURITY, RiskCategory.REPUTATION}
    medium_risk = {RiskCategory.BUSINESS, RiskCategory.BRAND, RiskCategory.OPERATIONAL}
    if categories & high_risk:
        return RiskLevel.CRITICAL if has_publication else RiskLevel.HIGH
    if categories & medium_risk:
        return RiskLevel.HIGH if has_publication else RiskLevel.MEDIUM
    return RiskLevel.MEDIUM if has_publication else RiskLevel.LOW
