# Permissions

Authorization is deny-by-default and requires both capability design and explicit permission. Tools declare required permissions and allowed agent types. Registration rejects an incompatible manifest; runtime authorization additionally intersects manifest tools with task tools.

Temporary grants are control-plane approved, limited to one agent, task, permission, and optional expiry. An agent cannot approve its own grant. Founder-only decisions—public content, permissions, deployment, brand, monetization, architecture, and registration approval—remain outside agents.
