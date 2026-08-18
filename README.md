# Pax Silica Intelligence

**Independent public-source intelligence on trusted technology, industrial capability, readiness, resilience, and the evidence behind them.**

**Explore:** [Live experience](https://bridgenode7.com/pax-silica/) · [Public data](data/) · [Credibility](docs/CREDIBILITY.md) · [Source correction](https://github.com/Bridge-Node-7/pax-silica/issues/new?template=public-source-correction.yml)

Verified public-source snapshot: **2026-08-15**

Published by **Bridge Node 7**. Not affiliated with or endorsed by the U.S. Department of State, the U.S. Government, or the Pax Silica initiative.

## Scope

This repository publishes:

- reviewed Pax Silica public-source records
- declaration-signatory and event state
- public program and policy records
- evidence and claim lineage
- Bridge Node 7 public analysis
- deterministic public site generation
- browser validation, deployment, and production verification

This repository does not establish qualification, certification, acquisition approval, mission readiness, government endorsement, or access to nonpublic information.

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

Sources and claims are separate records. Counts are derived. Time-sensitive facts include review dates. Historical states are superseded rather than silently erased.

## Public experience

The public learning path is:

```text
Participants
→ Technology
→ Capability
→ Philippines
→ Sustainability
→ Readiness
→ Resilience
→ Sources
```

The declaration-signatory map is explicitly scoped to declaration signatories. Broader participant categories require separate evidence and schema treatment.

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
PASS - evidence integrity
PASS - tests
PASS - repository gate
```

Preview:

```bash
python scripts/build_web.py --output build/web
python scripts/serve_preview.py --directory build/web --port 8765
```

Then open `http://127.0.0.1:8765/`.

## Evidence states

Canonical machine states remain:

`OFFICIAL` · `SECONDARY` · `REPORTED_DRAFT` · `BN7_ANALYSIS` · `UNKNOWN` · `SUPERSEDED`

The public site renders `reported_draft` as **Reported Development** so credible reporting remains visibly distinct without presenting it as settled official policy.

## Public boundary

**Public-source intelligence only.**

See [`docs/PUBLIC_BOUNDARY.md`](docs/PUBLIC_BOUNDARY.md).

## Repository map

```text
data/       reviewed public records and schemas
analysis/   Bridge Node 7 public analysis
web/        presentation templates and assets
scripts/    validation, build, preview, UAT, and production verification
tests/      repository and data tests
docs/       public intelligence, credibility, maintenance, and visual contracts
```

## Related public work

[Materials-to-Mission](https://github.com/Bridge-Node-7/materials-to-mission) · [Frontier Decision Engine](https://github.com/Bridge-Node-7/frontier-decision-engine) · [Frontier Intelligence Workflows](https://github.com/Bridge-Node-7/frontier-intelligence-workflows) · [BridgeNode7.com](https://bridgenode7.com/)

## License

Software and documentation are MIT licensed unless otherwise noted. Bridge Node 7 names, marks, website copy, and visual identity are not granted under that license.
