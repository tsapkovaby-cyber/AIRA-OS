# AIRA Academy production preview

Sprint 041 prepares the existing Next.js Academy/PWA for an HTTPS preview deployment without creating a second application.

## Runtime

- Build: `npm ci && npm run build`
- Start: `npm run start`
- Health endpoint: `GET /api/health`
- PWA start route: `/academy`

## Required preview environment

Set these values in the hosting provider's encrypted environment store. Never commit real values to GitHub.

- `AIRA_ACADEMY_BASE_URL` — canonical HTTPS preview URL after deployment.
- `AIRA_PREVIEW_OWNER_EMAIL` — temporary Owner/Developer preview credential.
- `AIRA_PREVIEW_OWNER_PASSWORD` — strong temporary Owner/Developer preview password.

Existing dashboard secrets remain separate (`AIRA_DASHBOARD_*`).

## Authorization boundary

`/developer` is fail-closed at middleware level. If preview owner credentials are absent, the route returns `401`; supplied credentials are checked server-side. This is a deployment-preview gate, not the final Academy account-role authentication system. Production student/owner authorization must continue to be derived from authenticated server-side account roles.

`/dashboard` keeps its existing session-token gate. Student plan entitlements never grant Owner/Developer access.

## PWA and caching

The service worker remains an application-shell/offline fallback mechanism. Authenticated lesson records, account data, Owner data, billing data, secrets, and authorization responses must not be intentionally cached for offline access.

## Search indexing

`/developer`, `/dashboard`, `/login`, and `/api` are excluded through the Next.js robots metadata route. This is not a security control; middleware/server authorization remains mandatory.

## Deployment acceptance checklist

1. Create a preview project from `tsapkovaby-cyber/AIRA-OS` and deploy the verified `main` revision.
2. Configure encrypted environment variables; do not paste secrets into repository files or PR comments.
3. Confirm HTTPS is active.
4. Confirm `/api/health` returns HTTP 200 and `status: ok`.
5. Confirm `/academy` loads and the PWA manifest/service worker are available.
6. Confirm `/developer` returns 401 without credentials and is accessible only with the configured Owner/Developer preview credentials.
7. Confirm `/dashboard` still requires its existing dashboard session.
8. Confirm Python Regression and Dashboard Regression are green for the deployed source SHA.

A custom public domain and final account-backed Owner authentication can be added after the first controlled preview is verified.
