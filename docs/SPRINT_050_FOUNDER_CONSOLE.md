# Sprint 050 — Founder Console & Academy Operations

Goal: turn `/developer` from a capability preview into a real founder operating console for AIRA Academy.

## Founder dashboard
- academy health and deployment status
- total students / active students / new students (data-source ready)
- lessons completed / completion rate / active streaks
- top languages and level distribution
- recent learning activity
- system alerts and items requiring attention

## Workspace sections
- Students: accounts, status, language, level, progress, last activity
- Learning content: languages, courses, lessons, publishing state
- Tutor & AI: tutor health, voice/video feature state, future model controls
- Analytics: acquisition, activation, engagement, retention and course completion
- Site operations: Academy links, health endpoint, release/deployment information and feature flags
- Billing: subscription/revenue placeholders until payments are integrated
- Security: owner session, audit events and access controls
- Settings: Academy defaults, supported languages and operational configuration

## Principles
- Owner tools remain isolated from the student subscription model.
- Statistics must come from server-side data sources once student accounts/cloud storage land.
- Until a data source exists, values must be clearly labelled as unavailable/demo rather than fabricated production metrics.
- Destructive actions require explicit confirmation.
- Mobile view remains usable, but desktop is the primary operations workspace.
