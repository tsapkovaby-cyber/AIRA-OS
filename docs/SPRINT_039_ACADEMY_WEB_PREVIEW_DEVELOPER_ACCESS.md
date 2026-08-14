# Sprint 039 — Academy Web Preview & Developer Access

## Goal
Give AIRA Academy a browser-facing preview and establish a safe Owner / Developer access model before public deployment.

## Routes
- `/academy` — first Academy browser preview.
- `/developer` — developer-facing preview surface. Production deployment must protect this route server-side.
- Existing `/learn` remains the student learning application.

## Authorization model
Owner / Developer is an account authorization role, not a commercial subscription. `AccountRole.OWNER` is intentionally distinct from Free, Basic, Advanced and Premium plans. The hidden `PlanCode.OWNER` entitlement profile remains an internal all-access projection for Academy features.

Production rules:
1. Resolve Owner role from the authenticated server-side account/session.
2. Never accept `owner=true`, plan, role or entitlement elevation from browser input.
3. Do not expose owner enrollment, secrets or bootstrap credentials in GitHub or client bundles.
4. Audit privileged actions.
5. Keep commercial billing unable to purchase or grant Owner role.

## Deployment
This sprint prepares the web surface but does not invent a production URL. A deployment stage must configure hosting, environment secrets and a public/custom domain. Sprint 040 can package the same web application as an installable PWA rather than creating a separate learning product.
