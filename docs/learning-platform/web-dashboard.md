# Sprint 028 — Student Web Dashboard

The student experience lives under `/learn` and is deliberately separate from the existing Founder dashboard under `/dashboard`. This avoids weakening internal Founder controls while the public learning product evolves.

The web shell provides Dashboard, My Learning, Courses, Progress, AI Tutor, Profile and Settings surfaces. Sprint 027 remains the source-of-truth API boundary; browser pages must never accept a client-controlled `student_id`. Production HTTP/session transport is kept as an adapter concern rather than duplicating Python learning rules in React.

Current Sprint 028 UI can render without paid AI access. The AI Tutor surface is an entry point for Sprint 029. Course and profile screens are structured around the canonical Sprint 025/027 fields.

## Local development

Run `npm install`, then `npm run dev`, and open `/learn`. Validate production output with `npm test` and `npm run build`.

## Future monetization and media

Later platform phases may add tiered subscriptions, payment provider adapters, entitlement checks, video lessons featuring AIRA, and a developer/owner entitlement with access to every plan. Payment settlement destination must be configured only through the selected payment provider's secure merchant settings and server-side secrets; banking/payout details must never be committed to GitHub or exposed to the browser.
