# Approval UI

Approval detail exposes request identity, requester, time, risk, rationale, evidence, proposal, expected result, risks, affected systems, Guardian result, and recommendation. Content detail additionally shows platform, type, preview, references, disclaimer, history, and an accessible textual diff.

Available decisions are approve, reject, request revision, defer, and cancel. High-risk requests require a second confirmation. A comment is retained as project history. The UI must not optimistically show success: it waits for a server response and displays its audit or error reference.
