# Guardian Engine

Sprint 009 introduces Guardian as AIRA's independent quality, ethics, transparency, and governance layer. Guardian protects users, trust, knowledge quality, and the AIRA Constitution by preventing unsafe or low-quality public actions until issues are resolved.

This sprint is architecture only. It does not implement AI moderation, legal automation, external compliance services, automatic censorship, or production persistence.

## Responsibilities

Guardian is responsible for:

- validating information quality;
- verifying source completeness and review metadata;
- checking Constitution alignment;
- evaluating declared risk categories;
- requiring Founder approval for governed domains;
- auditing important actions;
- preventing unsafe publication;
- generating transparency reports;
- storing review, incident, correction, lesson, false-positive, and policy-update history in future memory adapters.

## Validation Pipeline

1. Input
2. Constitution check
3. Transparency check
4. Evidence check
5. Knowledge validation
6. Risk assessment
7. Brand validation
8. Publishing policy check
9. Founder approval, when required
10. Approved, rejected, blocked, escalated, or needs revision

## API Surface

The architecture exposes these operations through `GuardianEngine`:

- `review_workflow`
- `validate_content`
- `check_constitution`
- `evaluate_risk`
- `generate_report`
- `approve`
- `reject`
- `block`
- `archive_review`
- `search_reviews`

## Sprint Status

Guardian initializes, creates review objects, evaluates evidence and Constitution metadata, classifies risk, creates incidents for blocked execution, and generates transparency reports.
