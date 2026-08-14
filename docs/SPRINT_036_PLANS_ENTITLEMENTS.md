# Sprint 036 — Plans & Entitlements

## Goal
Create a billing-independent access-control foundation before real payments are introduced.

## Public plans
- Free — placement, previews, limited text tutor.
- Basic — core courses, progress, text tutor.
- Advanced — adds voice tutor and video lessons.
- Premium — adds the complete personalized learning experience and future premium features.

Pricing and currency amounts are deliberately NOT defined in this sprint. RUB, USD and EUR pricing will live in the future billing/catalog layer so regional prices can change without altering access rules.

## Owner / Developer access
`owner` is a hidden non-commercial plan with wildcard entitlement access. It must never be displayed as a purchasable plan. Production assignment must be server-side and restricted to an authenticated owner/admin identity; clients must never self-assign it.

## Billing boundary
No card data, payment credentials, checkout URLs, merchant accounts, webhooks, provider secrets, or payout destinations are introduced here. Future payment integrations will translate successful billing state into a plan assignment through a server-side adapter.

This keeps Stripe, regional processors, currencies, taxes, refunds, subscriptions and payout configuration replaceable and separate from the learning domain.
