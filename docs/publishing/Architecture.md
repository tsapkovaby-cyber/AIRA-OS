# Architecture

The domain contains values and errors without infrastructure dependencies.
Application services depend on ports for repositories, queue, approval, media,
credentials, audit, events, clock, adapters, and idempotency. Infrastructure
implements those ports. Per-publication locks prevent concurrent workers in the
reference process; a production repository must provide distributed durable
locking and transactional outbox semantics.

Flow: approved snapshot → queue → preflight → adapter → receipt → events.
Global pause prevents queue dispatch and preflight. Each campaign destination
is modeled as its own publication so partial results remain truthful.
