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

## UI changes

Changes to `web/`, build logic, or interaction logic require full browser UAT.

## Data-only changes

Data-only changes require schema/source/claim/freshness validation, deterministic build, and browser smoke checks.

## Automated intelligence watch

A daily GitHub Action checks high-volatility `review_by` dates and known source URLs. It opens or updates one maintenance issue when review is needed.

The watch never changes canonical intelligence and never publishes claims. External discovery may propose candidate updates, but human review is required before canonical data changes. After a reviewed merge, the existing CI, browser UAT, Pages deployment, and production readback update the live page automatically.

## Cross-platform text encoding

All repository Python text I/O is explicitly UTF-8. The CI gate runs on Ubuntu and Windows so platform-default encoding cannot silently change generated or tested text.
