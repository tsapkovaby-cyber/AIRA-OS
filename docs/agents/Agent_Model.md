# Agent Model

An agent manifest records ID, name, type, semantic version, status, description, role, constraints, capabilities, permissions, memory/tool scopes, autonomy, prompt reference, non-secret model configuration, owner, timestamps, health and approval metadata. Status follows registered → inactive → ready → busy → ready, with controlled pause, degradation, disablement, error, and retirement paths.

Capabilities express ability and never imply authorization. Autonomy is capped at level 3; level 4 is deliberately absent. Task and result dataclasses are the structured input/output contracts.
