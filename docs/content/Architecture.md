# Architecture

## Boundaries

The domain has no framework or model-vendor dependency. `ContentService` orchestrates repositories, rendering, duplicate policy, platform adaptation, brand validation, Guardian review, Founder approval, and events through Protocol ports. `AIProvider` is an optional provider-neutral generation boundary. Provider implementations belong outside Core.

The engine can produce `READY_TO_PUBLISH`, but deliberately exposes no publishing or credential port. Draft metadata defaults to private. Repository versions are append-only and sequential.

## Flow

1. Validate the brief and its evidence graph.
2. query related content and apply the duplicate decision;
3. render and platform-adapt without changing the supported conclusion;
4. validate brand policy and append draft version;
5. route to Guardian, then (only after approval) Founder;
6. produce `READY_TO_PUBLISH` only after both approvals.

Events contain identifiers and safe metadata, not content secrets. Infrastructure must emit provider name, duration, validation outcomes, and errors through its observability layer without logging draft bodies or secrets.
