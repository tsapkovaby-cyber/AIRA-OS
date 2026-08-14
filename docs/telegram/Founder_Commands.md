# Founder commands

Natural language is primary. The initial shortcuts are `/start`, `/status`,
`/brief`, `/research`, `/content`, `/approvals`, `/agents`, `/workflows`,
`/publishing`, `/incidents`, `/costs`, `/pause`, `/resume`, and `/help`.

Commands are forwarded unchanged to Core. Status, briefs, knowledge, memory,
agent details and workflows are therefore generated from authoritative backend
state. `/pause` only requests Core to present pause options; it never pauses a
component in the command handler. Agent control, publishing control, global pause
and emergency stop require explicit confirmation generated and validated by Core.
