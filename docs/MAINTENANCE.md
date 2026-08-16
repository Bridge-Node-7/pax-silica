# Maintenance

Routine intelligence updates are data-only.

## Normal update

1. Add or update a public source in `data/sources.json`.
2. Add or update the related record in `data/pax-silica.json`.
3. Run `python scripts/check_repo.py`.
4. Review the generated preview in `build/web/`.
5. Open a PR.
6. Merge only after intelligence review and CI.
7. Pages deploys and production readback verifies the public bytes.

Do not edit generated public files.

## Freshness

High-volatility active records use `review_by`. Validation fails when `review_by` is earlier than the snapshot's `verified_through` date.

An automated field-level verification must not advance the global `snapshot.verified_through` date. Only a whole-snapshot review may advance that baseline.

## UI changes

Changes to `web/`, build logic, or interaction logic require full browser UAT.

## Data-only changes

Data-only changes require schema/source/claim/freshness validation, deterministic build, and browser smoke checks.

## Automated intelligence watch

A daily GitHub Action checks high-volatility `review_by` dates and known source URLs. It opens or updates one maintenance issue when review is needed.

The watch never changes canonical intelligence and never publishes claims. External discovery may propose candidate updates, but human review is required before canonical data changes. After a reviewed merge, the existing CI, browser UAT, Pages deployment, and production readback update the live page automatically.

## Cross-platform text encoding

All repository Python text I/O is explicitly UTF-8. The CI gate runs on Ubuntu and Windows so platform-default encoding cannot silently change generated or tested text.

## Live Intelligence v0.2.0

The v0.2.0 automation layer separates AI discovery from publication authority.

- The model receives canonical public records and a bounded monitoring policy.
- Web content is untrusted input and cannot supply instructions to the automation.
- Model output must match `automation/candidate.schema.json`.
- Deterministic Python policy decides `no_change`, `human_review`, or `auto_publish`.
- Autonomous publication is limited to explicitly enumerated rules in `automation/live-intelligence-policy.json`.
- A model-returned source identity is never publication proof; an autonomous rule must independently re-fetch and verify the authoritative record before application.
- Human-review candidates do not alter canonical intelligence.
- No-change scans create audit evidence without repository commits.

### Automated source-health states

- `ok` — automated retrieval returned a usable response.
- `manual_verification` — automation was blocked or rate-limited; this is not evidence that the source disappeared.
- `temporary_error` — a transient network or server condition prevented an automated determination.
- `unavailable` — a strong removal signal such as HTTP 404 or 410 requires human review.

Review deadlines and `unavailable` sources require review. Automated blocking or temporary transport failure alone must not silently invalidate canonical evidence.
