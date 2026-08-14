# Content Model

`Content` carries identity, type, topic, objective, audience, platform, BCP-47-style language string, status, timestamps, author, research/knowledge/source references, confidence, body, CTA, disclaimer, both review states, version, parent/campaign/analytics links, claims, and private workflow metadata.

A `ContentBrief` requires topic, why-now rationale, audience, problem, insight, evidence, goal, platform, format, tone, CTA, sources, risks, and optional required disclaimer.

Each `EvidenceClaim` is typed as fact, test result, AIRA opinion, estimate, prediction, or unverified information. Fact and test claims require known sources; test results additionally require an experiment ID. The source → claim links plus research and knowledge IDs make provenance reconstructable.
