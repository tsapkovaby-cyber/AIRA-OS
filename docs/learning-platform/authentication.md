# Authentication

Sprint 026 adds transport-independent student authentication. Passwords are hashed with PBKDF2-HMAC-SHA256 (310k iterations) through an upgradeable hasher boundary; plaintext passwords are never stored. Opaque session, recovery and verification tokens are generated with `secrets`, stored only as SHA-256 digests, expire, and support revocation/single-use semantics.

The service intentionally avoids JWT and any external auth SaaS so future adapters can add Google, Apple, Telegram, Auth0, Clerk or Supabase without rewriting the account domain.
