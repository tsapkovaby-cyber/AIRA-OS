# Accounts Domain

`UserAccount` is separate from Sprint 025 `Student`. `StudentAccountLink` connects authenticated accounts to learning identities and enables future parent→children and teacher relationships. Email identities are normalized case-insensitively. Account states are pending verification, active, disabled, deletion requested and deleted.

Founder/internal authorization remains separate from ordinary student accounts. Sprint 026 changes no Telegram or Railway runtime. Account deletion is modeled explicitly so future grace periods, export and retention rules can be implemented without replacing the domain.
