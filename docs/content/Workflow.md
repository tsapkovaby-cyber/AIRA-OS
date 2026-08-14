# Workflow and Approval

The legal state transitions prevent a draft from jumping to Founder review or readiness. Guardian approval is required to enter Founder review. Both approvals are required for approved/readiness states. `PUBLISHED` is intentionally rejected inside the Content domain.

Rejection is terminal except archival. A requested revision creates an append-only next version, resets both approvals, and returns to draft. Earlier versions remain retrievable. Only requested dimensions should be changed unless evidence correction requires broader edits.

Missing evidence, unknown sources, fabricated tests, material conflict, insufficient confidence, constitutional violations, or absent context must stop generation; callers should represent pre-draft cases as `RESEARCH_REQUIRED` rather than inventing material.
