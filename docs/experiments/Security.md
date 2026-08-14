# Security, Permissions, and Cost Controls

The executor receives no ambient provider access. Every test case declares required
tools and the experiment declares approved permissions; mismatch denies execution and
emits an audit event. High/critical risk, explicit approval requirements, and costs
above the configured threshold require Founder approval. The engine never purchases
credits or subscriptions.

Unknown code, destructive actions, external writes, sensitive uploads, production
access, and new credentials must be classified for approval and isolated outside this
reference service. Sprint 017 performs no unrestricted automation or binary execution.
Asset confidentiality and access control belong to the asset-store adapter; checksums
provide integrity, not authorization or secrecy.
