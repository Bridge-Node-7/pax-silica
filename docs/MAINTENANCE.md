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

Public maintenance documentation should contain only what is necessary to reproduce and validate the public artifact. Nonpublic research, internal operating material, personal working context, and sensitive configuration do not belong in this repository.

## Cross-platform text encoding

Repository Python text I/O is explicitly UTF-8. Validation runs on supported Windows and Linux environments.
