# Guardian API

## `review_workflow(...)`

Runs the Guardian validation pipeline and returns a `Review`.

Required keyword inputs:

- `workflow`
- `review_type`
- `evidence`
- `constitution_principles`
- `risk_categories`
- `governed_domains`
- `has_publication`

## `validate_content(evidence)`

Checks evidence completeness for public claims.

## `check_constitution(principles)`

Checks whether required Constitution areas have documented workflow review coverage.

## `evaluate_risk(categories, has_publication)`

Classifies declared risk categories into low, medium, high, or critical risk.

## `generate_report(review)`

Creates a transparency report with evidence summary, confidence, sources used, research date, review date, known limitations, and reviewer.

## Review Actions

- `approve(review_id)`
- `reject(review_id, reason)`
- `block(review_id, reason)`
- `archive_review(review_id)`
- `search_reviews(workflow=None)`
