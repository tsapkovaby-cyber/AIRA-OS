# Digital Human Engine

Sprint 018 separates AIRA's underlying character, canonical **visual identity**, and variable **brand styling**. `AIRA_MASTER_REFERENCE_V1` is the authoritative Founder-approved visual anchor. It is stored through Asset Storage as a hash and protected file reference—not as a database binary, provider ID, prompt, temporary URL, or repository-generated replacement.

## Architecture

`DigitalHumanProfile` composes visual identity with core and behavior identity while reserving voice and motion for later sprints. `DigitalHumanEngine` builds layered prompts, routes only to approved capable providers, persists every candidate and lineage link, evaluates identity separately from quality, invokes Guardian, and sends passing work to Founder review. Identity remains above providers.

Pipeline: request → identity lock → layered prompt → approved provider route → Asset Storage metadata → identity/quality evaluation → Guardian → Founder → approved asset.

## Invariants

- One ACTIVE identity; APPROVED/ACTIVE requires Founder approval.
- Master references are Founder-approved, read-only, immutable metadata.
- Generated content never promotes itself; Founder promotion creates a new reference.
- Founder rejection overrides every automated score and is retained as feedback.
- Identity below 70 is rejected regardless of quality; thresholds are configurable.
- Edits create child assets; originals are never overwritten.
- Canonical references are sent only to approved providers required by an approved request.
