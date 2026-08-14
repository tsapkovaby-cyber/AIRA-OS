# Content Intelligence Engine

Sprint 010 implements a provider-independent engine that turns verified research, knowledge, and recorded experience into **private drafts**. It is not a publisher or strategist. Public candidates follow `Draft → Guardian → Founder → Ready to Publish`; another future bounded context owns publishing.

The package is split into domain models and events, application orchestration, ports, policies, adapters, and tests. Russian (`ru`) is the request default; language is explicit so future locales do not require a model change.
