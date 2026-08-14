from guardian_engine import ClaimType, EvidenceRecord, GuardianEngine, ReviewResult, RiskCategory, RiskLevel


def complete_evidence():
    return [
        EvidenceRecord(
            claim="Guardian requires evidence for public claims.",
            claim_type=ClaimType.FACT,
            primary_source="AIRA Constitution",
            secondary_source="Sprint 009 specification",
            publication_date="2026-07-16",
            confidence=0.95,
            verification_status="Verified",
            supporting_references=("S009",),
        )
    ]


def complete_principles():
    return {"mission", "values", "ethics", "transparency", "safety", "evidence"}


def test_guardian_initializes():
    engine = GuardianEngine()
    assert engine.reviewer == "Guardian Engine"
    assert engine.reviews == {}
    assert engine.incidents == {}


def test_constitution_validation_reports_missing_checks():
    issues = GuardianEngine().check_constitution({"mission"})
    assert issues
    assert issues[0].category == "Constitution"
    assert issues[0].severity == RiskLevel.HIGH


def test_evidence_validation_requires_sources():
    evidence = [
        EvidenceRecord(
            claim="Unsupported claim",
            claim_type=ClaimType.FACT,
            primary_source=None,
            secondary_source=None,
            publication_date=None,
            confidence=0.7,
            verification_status="Unverified",
        )
    ]
    issues = GuardianEngine().validate_content(evidence)
    assert any(issue.category == "Evidence" for issue in issues)


def test_risk_classification_escalates_public_legal_risk():
    risk = GuardianEngine().evaluate_risk({RiskCategory.LEGAL}, has_publication=True)
    assert risk == RiskLevel.CRITICAL


def test_approval_workflow_requires_founder_for_brand_domain():
    review = GuardianEngine().review_workflow(
        workflow="Public brand announcement",
        review_type="Brand Validation",
        evidence=complete_evidence(),
        constitution_principles=complete_principles(),
        risk_categories={RiskCategory.BRAND},
        governed_domains={"brand"},
        has_publication=True,
    )
    assert review.result == ReviewResult.ESCALATED
    assert review.approval_status.value == "Pending Founder Approval"


def test_incident_created_when_guardian_blocks_publication():
    engine = GuardianEngine()
    review = engine.review_workflow(
        workflow="Legal public statement",
        review_type="Legal Review",
        evidence=complete_evidence(),
        constitution_principles=complete_principles(),
        risk_categories={RiskCategory.LEGAL},
        governed_domains={"legal"},
        has_publication=True,
    )
    assert review.result == ReviewResult.BLOCKED
    assert len(engine.incidents) == 1
    incident = next(iter(engine.incidents.values()))
    assert incident.notify_founder is True


def test_policy_enforcement_blocks_publication_without_evidence():
    review = GuardianEngine().review_workflow(
        workflow="Unsourced publication",
        review_type="Evidence Validation",
        evidence=[],
        constitution_principles=complete_principles(),
        risk_categories={RiskCategory.EDUCATIONAL},
        governed_domains=set(),
        has_publication=True,
    )
    assert review.result == ReviewResult.NEEDS_REVISION
    assert review.issues[0].category == "Evidence"


def test_transparency_report_contains_required_fields():
    engine = GuardianEngine()
    review = engine.review_workflow(
        workflow="Educational content",
        review_type="Transparency Report",
        evidence=complete_evidence(),
        constitution_principles=complete_principles(),
        risk_categories={RiskCategory.EDUCATIONAL},
        governed_domains=set(),
        has_publication=True,
    )
    report = engine.generate_report(review)
    assert "Evidence Summary:" in report
    assert "Confidence:" in report
    assert "Sources Used:" in report
    assert "Known Limitations:" in report
    assert "Reviewer:" in report
