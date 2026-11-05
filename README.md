# Pax Silica Intelligence

Independent public-source intelligence on Pax Silica, strategic technology supply chains, qualification, and resilient capability.

Pax Silica Intelligence turns reviewed public evidence into an inspectable view of participants, technology dependencies, industrial capability, readiness, resilience, and supporting sources—claims, sources, review dates, and unknowns kept as separate fields.

[Live experience](https://bridgenode7.com/pax-silica/) · [Latest release](https://github.com/Bridge-Node-7/pax-silica/releases/latest) · Local gate: `python3 scripts/check_repo.py` · [Partner](https://bridgenode7.com/partner/)

## Contents

- `data/` — reviewed public-evidence corpus (`pax-silica.json`, `sources.json`, schemas, evidence baseline)
- `web/` — static public experience generated from that corpus
- `scripts/` — validation, integrity, and deterministic site/release generation (`check_repo.py` is the gate)
- `docs/` — credibility and source-state conventions

Generation is deterministic. Records stay inspectable.

## Local preview

Requires Python 3.11+ (`python3`). Prefer an out-of-tree virtualenv:

```bash
python3 -m venv ../pax-venv
source ../pax-venv/bin/activate
python3 -m pip install -r requirements-browser.txt  # only if running browser checks
python3 scripts/check_repo.py
python3 scripts/serve_preview.py   # optional local static preview when present
```

## Evidence classes

- **Official** — authoritative public publication
- **Secondary** — independent context or corroboration
- **Reported Development** — credible reporting not established here as settled final policy
- **Analysis** — Bridge Node 7 interpretation
- **Unknown** — not adequately established
- **Superseded** — a historical state replaced by a newer record

The public snapshot date identifies the corpus review boundary. Individual evidence records show when they were reviewed. Time-sensitive fields are dated observations.

## Validation

```bash
python3 scripts/check_repo.py
```

The gate checks canonical data, publication checks, readability, deterministic generation, evidence integrity, and regression tests.

## Assurance boundary

Public-source research separates reported claims from supporting sources, dates, and unresolved questions. Supplier qualification, investment merit, mission readiness, and authorization to act remain with accountable human processes.

## Release

`main` is the current reviewed source. Distribution identity lives on Releases and in CHANGELOG.

## Corrections

Public-source corrections may be proposed through the repository’s source-correction issue form. Submit public-source information only.

## License

MIT License. See `NOTICE` for project identity, non-affiliation, and marks.
