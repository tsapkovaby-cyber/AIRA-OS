# Security

The framework fails closed for unknown agents, tools, prompts, permissions, memory scopes, invalid lifecycle transitions, non-Workflow execution, and Guardian blocks. Agents cannot self-register, delegate, self-grant, modify manifests/prompts, approve output, impersonate Founder, or override the Constitution.

All execution is auditable. Repeated failures degrade and then mark an agent unhealthy for control-plane action. Global pause prevents new starts. Implementations should sandbox filesystem/network and raise incidents for forbidden tools/memory, schema failures, bypass attempts, unapproved publication, or policy violations.
