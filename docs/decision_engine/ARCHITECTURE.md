# Decision Engine Architecture Report

## Mission

The Decision Engine transforms information into responsible actions. Every decision is designed to be explainable, reproducible, auditable, reversible, and subject to Founder control.

## Pipeline

1. Receive request.
2. Identify intent.
3. Determine context.
4. Collect knowledge.
5. Collect memory.
6. Check Constitution.
7. Evaluate confidence.
8. Generate alternatives.
9. Estimate risk.
10. Select best option.
11. Run Guardian validation.
12. Request Founder approval when required.
13. Execute only outside this Sprint 006 architecture scope.
14. Store decision.

## Decision Object

A decision contains:

- Decision ID and timestamp.
- Decision type and goal.
- Context and inputs.
- Alternatives and selected option.
- Confidence and confidence band.
- Risk classification.
- Reasoning and constitution checks.
- Required approval and execution status.
- Immutable-style history events appended over time.

## Confidence Model

- 95–100: Verified.
- 90–95: Highly reliable.
- 75–90: Reliable.
- 50–75: Needs verification.
- Below 50: Do not recommend.

## Risk Model

Risk is classified as minimal, low, medium, high, or critical. The reference classifier scores impact, reversibility, and external exposure on a 1–5 scale. High and critical decisions require Founder approval.

## Approval Matrix

Auto-executable architecture candidates are limited to low-risk internal tasks. Founder approval is required for publishing, strategic, business, security, architecture-sensitive, brand-sensitive, monetization, external communication, and constitution-changing decisions. Publishing is never automatic.

## Explainability

Each explanation answers:

- Why this option was selected.
- Which inputs and evidence were used.
- What confidence applies.
- Which alternatives were considered.
- Why approval is or is not required.
