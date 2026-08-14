# Research Engine Architecture Report

Sprint 005 introduces an architecture-only Research Engine. The engine discovers, collects, classifies, verifies, normalizes, scores, and forwards research candidates to the Knowledge Engine. It never publishes, schedules jobs, scrapes websites, automates browsers, calls production APIs, or makes final conclusions.

## Pipeline

1. Discovery
2. Collection
3. Classification
4. Source Verification
5. Duplicate Detection
6. Normalization
7. Confidence Evaluation
8. Knowledge Candidate
9. Knowledge Engine handoff

The implemented `ResearchPipeline` stops at `KnowledgeCandidate`, preserving the rule that research precedes knowledge and does not become a recommendation or publication.

## Core Models

- `Source`: source name, URL, category, trust level, and verification state.
- `ResearchItem`: metadata, trust, confidence, references, freshness, duplicate links, conflicts, history, and security context.
- `ResearchScore`: source quality, evidence quality, practical importance, business impact, educational value, novelty, and confidence.
- `KnowledgeCandidate`: immutable handoff object for the Knowledge Engine boundary.

## Trust Model

- Level A: official and academic sources.
- Level B: developer, industry, and internal sources.
- Level C: community and experimental sources.
- Level D: supported by the model, but unverified claims are not treated as facts.

## Duplicate Detection

Duplicates are detected by normalized title, normalized source URL, and information category. Duplicate records are linked through `duplicate_of` and `duplicate_links`; they are not removed so the historical chain is preserved.

## Conflict Handling

Conflicts are recorded bidirectionally between research items. The engine stores both records, logs the disagreement in history, and leaves resolution to downstream Knowledge Engine review.

## Security

Every item includes an owner, visibility, permissions, source verification state, and history. This is architecture-level metadata only; policy enforcement can be added in future sprints.

## Interfaces

The architecture includes an in-memory `ResearchAPI` with methods for create, update, archive, search, export, import, validate, summarize, and forwarding a research candidate.

## Future Improvements

- Hourly monitoring.
- Daily digests.
- Weekly reviews.
- Monthly reports.
- Manual triggers.
- Production data connectors after Founder approval.
