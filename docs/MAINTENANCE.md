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


## Low-resistance maintenance

Evidence-only changes stay data-first: update canonical records, run the repository gate, inspect the generated output, and publish only reviewed changes. Interface changes add browser validation but do not require intelligence data to change.

The evidence baseline is a floor, not a frozen current count. Canonical active signatories determine the rendered count; map and roster identity must remain exactly aligned with that canonical set. Geographic display coordinates live in `web/map-display.json`, so a reviewed network addition updates data rather than Python code.

Freshness validation reports every stale record in one run. A due-soon notice is informational; the `review_by` date remains the hard re-review boundary.

Source identifiers are persistent and may be non-contiguous. Never reuse an identifier. Record retirement or supersession only when a record actually existed and its evidence state changes.

External authoritative sites can be temporarily unavailable. URL structure, HTTPS, allowed-host policy, source identity, and internal evidence linkage remain hard checks. Remote reachability is not a required release gate.

## Visual maintenance

Interface-affecting changes require machine geometry checks plus review of the retained 390 px and 1440 px Chromium screenshots. Machine checks establish invariants; human review judges hierarchy, breathing room, typography, coherence, and visual polish.

## Dormant operation

The published site is a static reviewed snapshot and remains usable without routine edits. The visible snapshot date makes evidence age explicit. Scheduled freshness validation is read-only: it can flag aging time-sensitive records, but it does not mutate, unpublish, or rewrite production.

## Public minimization

Keep only evidence provenance, public product identity, the approved contact channel, and instructions required to build, validate, and publish. Do not add individual background, unrelated affiliations, social profiles, or non-evidence external references.
