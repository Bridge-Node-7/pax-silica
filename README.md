# Pax Silica Intelligence

Independent public-source intelligence on Pax Silica, strategic technology supply chains, qualification, and resilient capability.

Stable public release — see the latest [GitHub Release](https://github.com/Bridge-Node-7/pax-silica/releases/latest). Quickstart: `python3 scripts/check_repo.py`. Collaboration: [GitHub Issues](https://github.com/Bridge-Node-7/pax-silica/issues).

Pax Silica Intelligence turns reviewed public evidence into an inspectable view of participants, technology dependencies, industrial capability, readiness, resilience, and supporting sources.

## Scope and limitations

This public-source research separates reported claims from supporting sources, dates and unresolved questions. It does not establish supplier qualification, investment merit, mission readiness or authorization to act.

## What this repository contains

- `data/` — reviewed public-evidence corpus (`pax-silica.json`, `sources.json`, schemas, evidence baseline).
- `web/` — static public experience generated from that corpus.
- `scripts/` — validation, integrity, and deterministic site/release generation (`check_repo.py` is the gate).
- `docs/` — credibility and source-state conventions used when classifying records.

Records stay inspectable: claims, sources, review dates, and unknowns are separate fields. Generation is deterministic; a passing gate establishes only what that gate tested.

## Local preview

Requires Python 3.11+ (`python3`). Prefer an out-of-tree virtualenv:

```bash
python3 -m venv ../pax-venv
source ../pax-venv/bin/activate
python3 -m pip install -r requirements-browser.txt  # only if running browser checks
python3 scripts/check_repo.py
python3 scripts/serve_preview.py   # optional local static preview when present
```

Or open the published experience at the public URL below after a reviewed release.

## Public experience

Explore the reviewed public-evidence snapshot at:

https://bridgenode7.com/pax-silica/

## Evidence

The public record distinguishes:

- **Official** — authoritative public publication.
- **Secondary** — independent context or corroboration.
- **Reported Development** — credible reporting not established here as settled final policy.
- **Analysis** — Bridge Node 7 interpretation.
- **Unknown** — not adequately established.
- **Superseded** — a historical state replaced by a newer record.

The overall public snapshot date identifies the corpus review boundary. Individual evidence records show when they were reviewed. Time-sensitive status fields are dated observations, not continuously live status. Later developments are not implied.

## Trust boundary

Sources and claims remain separately inspectable. Analysis is labeled. Unknowns remain unknown.

Public inclusion does not imply endorsement, qualification, certification, validation, investment merit, mission readiness, or authority to act.

The public site is generated from reviewed records and validated before publication.

## Validation

Run:

```bash
python3 scripts/check_repo.py
```

The repository gate checks canonical data, publication checks, readability, deterministic generation, evidence integrity, and regression tests.

A passing control establishes only what that control tested.

## Release status

`main` is the current reviewed source. GitHub Releases are stable distribution milestones and may intentionally lag reviewed maintenance on `main`. A source version ahead of the latest GitHub Release is unreleased until a release is published.

## Corrections

Public-source corrections may be proposed through the repository's source-correction issue form. Submit public-source information only.

## License and notice

Software is provided under the MIT License. See `NOTICE` for project identity, non-affiliation, and marks.
