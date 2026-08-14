# AIRA Learning Platform Roadmap

- Sprint 025 — Learning Platform Foundation
- Sprint 026 — Authentication & Student Accounts
- Sprint 027 — Learning Platform API
- Sprint 028 — Student Web Dashboard
- Sprint 029 — AI Tutor Integration
- Sprint 030 — Conversational Practice
- Sprint 031 — Adaptive Learning & Student Memory
- Sprint 032 — Assessments & Placement Testing
- Sprint 033 — Voice Tutor
- Sprint 034 — Course Authoring / Admin
- Sprint 035 — Platform Beta
- Future Monetization — tiered plans, subscriptions, entitlements, owner/developer all-access, payment-provider integration and secure payout configuration
- Future Media Learning — AIRA-led video lessons, lesson media library, captions/transcripts and entitlement-aware video access

Monetization must be implemented behind provider-independent billing/entitlement ports. The developer/owner account can receive a non-billable internal entitlement granting all plan capabilities without weakening normal user authorization. Payment payout/bank details belong only in the payment provider's secure merchant configuration and environment/secrets management, never in repository source or browser code.

Each sprint must reuse AIRA OS capabilities, preserve student isolation, keep external AI optional in deterministic tests, and ship through a reviewed PR before promotion to `main`.
