# Master Voice Reference

`AIRA_MASTER_VOICE_REFERENCE_V1` is registered as the active, Founder-approved,
read-only `MASTER_VOICE_REFERENCE` for AIRA and points to protected secure ingest.
Its actual checksum remains `PENDING_SECURE_INGEST` until the supplied binary is
placed in protected storage; no recording binary was present in this repository.

Ingest must calculate SHA-256 without modifying the file, restrict access, and
replace only the pending checksum metadata—not the recording. Every derivative is
a separately hashed child. Provider upload requires policy review and must never
be triggered by discovery alone.
