# Publication Model

`Publication` records identity, immutable content version, workflow,
destination/account/type, lifecycle status, UTC schedule/request/publication
times, intended timezone, approval IDs, adapter, external ID, idempotency key,
retry/error data, and audit history. `PublicationReceipt` records the external
ID, platform, account, version, timestamp, checksum, safe metadata, and optional
public URL. Published records cannot be cancelled or silently changed.
