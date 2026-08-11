# Approval Policy

Queue admission and immediate preflight both require Guardian **APPROVED**,
Founder **APPROVED**, matching content IDs and versions, and content
**READY_TO_PUBLISH**. Any content modification creates a new version and makes
old approvals unusable. A failure blocks execution and creates an audit event.
Scheduling never substitutes for approval. External deletion requires a
separate explicit Founder approval and is disabled in Sprint 011.
