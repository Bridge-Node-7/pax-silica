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

## Assistive-technology evidence boundary

Automated browser, keyboard, forced-color, reflow, and no-JavaScript checks do not establish real screen-reader behavior. A release record may claim NVDA or VoiceOver coverage only when a human-run assistive-technology session has been completed and retained as release evidence.


## Visual release evidence

For interface-affecting changes, Browser UAT must prove responsive geometry, interaction behavior, no-JavaScript resilience, and section-header separation. The retained Chromium `mobile-full.png` and `desktop-full.png` images receive one human visual review before public merge.

A machine PASS does not by itself establish luxurious visual quality. Human visual review is deliberately narrow: hierarchy, spacing, typography, coherence, and obvious rendering defects.
