# Evidence

Evidence records store a type, asset-storage reference, SHA-256 checksum, source,
test-case link, timestamp, metadata, and confidentiality level. Raw bytes and large
media are never embedded. `verify_evidence` detects later asset modification. Evidence
is append-only through the service API; evaluation and Guardian review do not mutate
it. Failed, timeout, invalid, and partial executor outputs remain attached to their
test cases and appear in reports.
