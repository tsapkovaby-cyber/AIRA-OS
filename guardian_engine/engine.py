"""Guardian Engine orchestration architecture."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from .models import EvidenceRecord, Incident, Review, ReviewResult, RiskCategory, RiskLevel, ValidationIssue, highest_risk
from .policies import check_constitution_alignment, classify_risk, requires_founder_approval, validate_evidence


@dataclass
class GuardianEngine:
    """Independent quality, ethics, transparency, and governance layer.

    The engine stores in-memory architecture artifacts for sprint validation. It
    can be replaced by persistence adapters in future implementation sprints.
    """

    reviewer: str = "Guardian Engine"
    reviews: dict[str, Review] = field(default_factory=dict)
    incidents: dict[str, Incident] = field(default_factory=dict)
    transparency_logs: list[str] = field(default_factory=list)

    def review_workflow(
        self,
        *,
        workflow: str,
        review_type: str,
        evidence: list[EvidenceRecord],
        constitution_principles: set[str],
        risk_categories: set[RiskCategory],
        governed_domains: set[str],
        has_publication: bool = False,
    ) -> Review:
        """Run the architecture validation pipeline and return a review object."""

        issues: list[ValidationIssue] = []
        issues.extend(check_constitution_alignment(constitution_principles))
        issues.extend(validate_evidence(evidence) if has_publication else [])

        assessed_risk = max(
            classify_risk(risk_categories, has_publication),
            highest_risk(issues),
            key=self._risk_rank,
        )
        approval_status = requires_founder_approval(governed_domains)
        result = self._decide_result(issues, assessed_risk, approval_status)
        review = Review(
            workflow=workflow,
            reviewer=self.reviewer,
            review_type=review_type,
            result=result,
            confidence=self._confidence_from_issues(issues),
            risk=assessed_risk,
            issues=issues,
            recommendations=[issue.recommendation for issue in issues if issue.recommendation],
            approval_status=approval_status,
            evidence=evidence,
        )
        review.add_history("Validation pipeline completed.")
        self.reviews[review.review_id] = review
        self.transparency_logs.append(self.generate_report(review))

        if review.is_blocking:
            self.create_incident(review, "Guardian blocked workflow pending resolution.")
        return review

    def validate_content(self, evidence: list[EvidenceRecord]) -> list[ValidationIssue]:
        """Validate content evidence requirements."""

        return validate_evidence(evidence)

    def check_constitution(self, principles: set[str]) -> list[ValidationIssue]:
        """Validate workflow alignment with the AIRA Constitution checklist."""

        return check_constitution_alignment(principles)

    def evaluate_risk(self, categories: set[RiskCategory], has_publication: bool) -> RiskLevel:
        """Evaluate declared risk categories."""

        return classify_risk(categories, has_publication)

    def approve(self, review_id: str) -> Review:
        """Approve a review after outstanding requirements are resolved."""

        review = self.reviews[review_id]
        review.result = ReviewResult.APPROVED
        review.add_history("Review approved.")
        return review

    def reject(self, review_id: str, reason: str) -> Review:
        """Reject a review and create an incident for auditability."""

        review = self.reviews[review_id]
        review.result = ReviewResult.REJECTED
        review.add_history(f"Review rejected: {reason}")
        self.create_incident(review, reason)
        return review

    def block(self, review_id: str, reason: str) -> Incident:
        """Block a workflow until issues are resolved."""

        review = self.reviews[review_id]
        review.result = ReviewResult.BLOCKED
        review.add_history(f"Review blocked: {reason}")
        return self.create_incident(review, reason)

    def archive_review(self, review_id: str) -> Review:
        """Mark a review as archived in its immutable history trail."""

        review = self.reviews[review_id]
        review.add_history("Review archived.")
        return review

    def search_reviews(self, workflow: str | None = None) -> list[Review]:
        """Search reviews by workflow name or return all reviews."""

        if workflow is None:
            return list(self.reviews.values())
        return [review for review in self.reviews.values() if review.workflow == workflow]

    def create_incident(self, review: Review, reason: str) -> Incident:
        """Create an incident, notify Founder by flag, and store history."""

        incident = Incident(
            review_id=review.review_id,
            reason=reason,
            risk=review.risk,
            suggested_resolution="Resolve Guardian review issues and request Founder approval if required.",
        )
        incident.add_history("Incident created and Founder notification required.")
        self.incidents[incident.incident_id] = incident
        return incident

    def generate_report(self, review: Review) -> str:
        """Generate a transparency report suitable for publication metadata."""

        sources = [record.primary_source for record in review.evidence if record.primary_source]
        limitations = "; ".join(issue.message for issue in review.issues) or "No known limitations recorded."
        return "\n".join(
            [
                f"Review ID: {review.review_id}",
                f"Workflow: {review.workflow}",
                f"Evidence Summary: {len(review.evidence)} evidence record(s)",
                f"Confidence: {review.confidence:.2f}",
                f"Sources Used: {', '.join(sources) if sources else 'None recorded'}",
                f"Research Date: {datetime.now(timezone.utc).date().isoformat()}",
                f"Review Date: {review.timestamp.date().isoformat()}",
                f"Known Limitations: {limitations}",
                f"Reviewer: {review.reviewer}",
            ]
        )

    def _decide_result(self, issues: list[ValidationIssue], risk: RiskLevel, approval_status) -> ReviewResult:
        if risk == RiskLevel.CRITICAL:
            return ReviewResult.BLOCKED
        if approval_status.value == "Pending Founder Approval":
            return ReviewResult.ESCALATED
        if any(issue.severity in {RiskLevel.HIGH, RiskLevel.CRITICAL} for issue in issues):
            return ReviewResult.NEEDS_REVISION
        if issues:
            return ReviewResult.APPROVED_WITH_NOTES
        return ReviewResult.APPROVED

    def _confidence_from_issues(self, issues: list[ValidationIssue]) -> float:
        return max(0.35, 1.0 - (0.15 * len(issues)))

    def _risk_rank(self, risk: RiskLevel) -> int:
        return {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, RiskLevel.HIGH: 2, RiskLevel.CRITICAL: 3}[risk]
