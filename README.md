# Pax Silica Intelligence

**Independent public-source intelligence on trusted technology ecosystems from critical materials to advanced computing, AI, quantum-enabling systems, qualification, and resilient supply.**

Live route when deployed: **https://bridgenode7.com/pax-silica/**

Verified seed snapshot: **2026-08-15**

Published by **Bridge Node 7**. Not affiliated with or endorsed by the U.S. Department of State, the U.S. Government, or the Pax Silica initiative.

Part of the Bridge Node 7 public frontier-intelligence ecosystem. It complements [Materials-to-Mission](https://github.com/Bridge-Node-7/materials-to-mission), [Frontier Decision Engine](https://github.com/Bridge-Node-7/frontier-decision-engine), [Frontier Intelligence Workflows](https://github.com/Bridge-Node-7/frontier-intelligence-workflows), and [BridgeNode7.com](https://bridgenode7.com/).

## What this repository owns

- Pax Silica public-source reference records
- signatory and event state
- public program and policy records
- evidence and claim lineage
- Bridge Node 7 Pax Silica analysis
- deterministic public site generation
- browser UAT, Pages deployment, and production verification

## What it does not own

- Materials-to-Mission qualification-method authority
- Frontier Decision Engine decision-method authority
- private Bridge Node 7 intelligence
- customer, supplier, controlled, classified, or export-controlled information

## Information model

```text
REFERENCE           CHANGE INTELLIGENCE          BN7 ANALYSIS
   │                        │                         │
   └─────────────── reviewed public records ─────────┘
                            │
                            ▼
                     deterministic build
                            │
                            ▼
               bridgenode7.com/pax-silica/
```

Sources and claims are separate records. Counts are derived. High-volatility facts carry freshness metadata. Historical states are superseded rather than silently erased.

## Validate

Requires Python 3.11+.

```bash
python scripts/check_repo.py
```

Expected:

```text
PASS - data integrity
PASS - freshness
PASS - public boundary
PASS - spoken-language audit
PASS - deterministic build
PASS - tests
PASS - repository gate
```

Preview:

```bash
python scripts/build_web.py --output build/web
python scripts/serve_preview.py --directory build/web --port 8765
```

Then open `http://127.0.0.1:8765/`.

## Routine intelligence update

1. Update `data/sources.json`.
2. Update the related reviewed record in `data/pax-silica.json`.
3. Run `python scripts/check_repo.py`.
4. Review the generated diff/preview.
5. Open a PR.
6. Merge after intelligence review and CI.
7. Pages deploys and verifies production.

Routine intelligence updates should not require editing HTML, CSS, or JavaScript.


## Intelligence watch

A daily GitHub Action checks review dates and known public-source health. When attention is needed, it opens or updates one review issue. It does not modify canonical intelligence or publish claims.

After a reviewed data change reaches `main`, CI, browser UAT, Pages deployment, and anonymous production readback handle publication.

## Evidence states

`OFFICIAL` · `SECONDARY` · `REPORTED / DRAFT` · `BN7 ANALYSIS` · `UNKNOWN` · `SUPERSEDED`

## Public boundary

**Public-source intelligence only.**

See [PUBLIC_BOUNDARY.md](docs/PUBLIC_BOUNDARY.md).

## Repository map

```text
data/       reviewed public records and schemas
analysis/   Bridge Node 7 analysis
web/        stable presentation templates and assets
scripts/    validation, build, preview, UAT, production verification
tests/      repository and data tests
docs/       intelligence model, maintenance, visual and release contracts
```

## License

Software and documentation are MIT licensed unless otherwise noted. Bridge Node 7 names, marks, website copy, and visual identity are not granted under that license.
