# Decision Engine

Sprint 006 introduces the Decision Engine architecture. The engine transforms evaluated evidence into responsible, auditable actions. It does not perform research, generate knowledge, run LLM inference, or execute external workflows.

## Responsibilities

- Identify the decision type and goal.
- Preserve context, inputs, alternatives, selected option, confidence, risk, reasoning, approval state, status, and history.
- Enforce evidence-first and constitution-first validation.
- Require Founder approval for high-risk or externally sensitive decisions.
- Explain every recommendation with evidence, alternatives, confidence, and risk.

## Non-Responsibilities

- No autonomous execution.
- No automatic publishing.
- No external integrations.
- No business workflow automation.
- No AI reasoning implementation.

## API Surface

The architecture exposes methods for creating, evaluating, storing, loading, explaining, approving, rejecting, cancelling, archiving, and searching decisions through `DecisionEngine` and `DecisionStore`.
