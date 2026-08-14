# Guardian Examples

```python
from guardian_engine import ClaimType, EvidenceRecord, GuardianEngine, RiskCategory

engine = GuardianEngine()
evidence = [
    EvidenceRecord(
        claim="Every public claim requires evidence.",
        claim_type=ClaimType.FACT,
        primary_source="AIRA Constitution",
        secondary_source="Sprint 009 specification",
        publication_date="2026-07-16",
        confidence=0.95,
        verification_status="Verified",
    )
]

review = engine.review_workflow(
    workflow="Educational publication",
    review_type="Knowledge Quality",
    evidence=evidence,
    constitution_principles={"mission", "values", "ethics", "transparency", "safety", "evidence"},
    risk_categories={RiskCategory.EDUCATIONAL},
    governed_domains=set(),
    has_publication=True,
)

print(review.result)
print(engine.generate_report(review))
```
