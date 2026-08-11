# Security

- No credentials are accepted by domain profiles or written to audit records.
- System secrets cannot enter prompts.
- Founder-private context requires explicit permission.
- Agents select task profiles, not arbitrary models.
- Disabled or unhealthy providers are excluded before scoring.
- External content remains an untrusted user-role message.
- Model tool requests are data only; execution remains the Tool Permission Layer's responsibility.

