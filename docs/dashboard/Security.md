# Dashboard Security

Dashboard routes are private by middleware. Sessions use HTTP-only, SameSite cookies, expiry, and secure transport in production. Mutation routes authenticate, authorize, validate with Zod, require CSRF proof, and return structured failures. Production deployment must add shared rate limiting and replace the local demonstration identity adapter.

Secrets are never embedded in frontend code or returned after entry; settings expose only configuration state and update time. Approval services must re-check Founder identity, role, object version, Guardian/workflow state, expiry, and replay nonce. Every sensitive result is audited. The frontend cannot publish or grant permissions directly.
