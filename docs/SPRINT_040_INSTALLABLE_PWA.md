# Sprint 040 — Installable AIRA Academy PWA

## Goal
Turn the Sprint 039 browser preview into an installable progressive web application without creating a second learning platform.

## Delivered
- Web app manifest with `/academy` as the start URL.
- Standalone display mode and AIRA Academy application identity.
- Regular and maskable application icons.
- Client-side service-worker registration.
- Small offline application shell and explicit `/offline` fallback.
- Regression tests for manifest and offline assets.

## Architecture
The PWA is only another shell over the existing AIRA Academy web application. It must continue to use the same authenticated account, learning APIs, progress, subscriptions, Tutor, Voice Tutor and video systems as the normal browser experience.

The service worker must never be treated as an authorization boundary. Sensitive account, Owner/Developer and paid-entitlement decisions remain server-side. Offline caching is for resilient application presentation; future authenticated offline lesson storage requires a separate privacy/security design before user data is cached locally.

## Deployment requirements
Installability requires production HTTPS (localhost is acceptable for development). A public Academy URL/domain is deliberately not introduced by this sprint. Native iOS/Android packaging and app-store publication remain later delivery stages.
