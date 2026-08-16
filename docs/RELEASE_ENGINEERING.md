# Release Engineering

The public site is built deterministically from reviewed source data and stable web templates.

## Gates

`python scripts/check_repo.py`

The gate validates:

- repository structure
- source IDs
- claim/source linkage
- dates and freshness
- evidence-state vocabulary
- public boundary patterns
- deterministic web build
- generated manifest
- unit tests

Browser UAT is a separate workflow.

GitHub Pages deployment builds a fresh `_site`, verifies the exact artifact set and manifest, deploys, then performs anonymous production readback against `https://bridgenode7.com/pax-silica/`.
