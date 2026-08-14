# Context Builder

Context blocks retain source ID, version, confidence, freshness status, and passage. Selection is
score ordered and token-budget bounded using a conservative character estimate. Oversized evidence
is skipped without crashing. Conflict markers remain explicit. Constitution and task instructions
remain the responsibility of Sprint 015's outer context builder and precede this evidence block.

