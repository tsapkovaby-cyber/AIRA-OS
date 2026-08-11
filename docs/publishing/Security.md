# Security

Accounts hold opaque credential references only. A secrets provider reports
credential availability; raw keys, tokens, passwords, and refresh tokens must
never enter domain objects, Git, prompts, events, logs, or unencrypted dumps.
Use least-privilege platform credentials and encrypt secrets at rest. Disabled
accounts and unavailable adapters fail closed. Log only identifiers, status,
duration, safe error categories, and retry number.
