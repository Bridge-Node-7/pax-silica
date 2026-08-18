# Maintenance

Public updates should remain data-first and evidence-bound.

## Public data changes

1. Update the reviewed public source in `data/sources.json`.
2. Update the related reviewed record in `data/pax-silica.json`.
3. Run `python scripts/check_repo.py`.
4. Review the generated public output before publication.

Do not edit generated public files directly.

## Freshness

High-volatility active records use `review_by`. Validation fails when a review deadline falls behind the verified public snapshot.

A field-level verification must not silently advance the verification date of unrelated records.

## Interface changes

Changes to `web/`, build logic, or interaction logic require browser validation.

## Public boundary

Only material approved for public release belongs in the repository. Keep maintenance guidance focused on reproducibility, validation, and user-relevant limitations.

## Cross-platform text encoding

Repository Python text I/O is explicitly UTF-8. Validation runs on supported Windows and Linux environments.

## Freshness execution

The repository runs a read-only scheduled freshness check in addition to pull-request and push validation. The scheduled check evaluates existing reviewed records only. It does not collect new intelligence, promote evidence states, edit canonical data, or publish content.
