# AIRA Agent Framework

Agents are registered, specialized workers; they are not AIRA Core and cannot redefine AIRA identity. The registry is authoritative: an unknown agent cannot execute. Planner and Workflow assign tasks, Guardian may block them, and Founder controls approvals and overrides.

The implementation separates immutable domain contracts, registry and lifecycle, authorization, controlled runtime, health policy, prompts, and provider routing under `backend/agents`. No real credentials, browsing, publishing, shell, unrestricted filesystem, direct agent messaging, or self-modification is included.
