# Live Intelligence

Pax Silica Live Intelligence is an evidence-governed automation layer for public-source monitoring.

## Authority boundary

```text
PUBLIC SOURCES
    ↓
AI DISCOVERY + STRICT EXTRACTION
    ↓
STRUCTURED CANDIDATE
    ↓
DETERMINISTIC POLICY
    ├── NO_CHANGE → audit only
    ├── HUMAN_REVIEW → issue / review queue
    └── AUTO_PUBLISH → bot PR → required V&V → merge → Pages → production attestation
```

The model never receives the GitHub App installation token and never chooses repository paths, shell commands, merge policy, or publication authority.

Model-reported source IDs and URLs are not accepted as proof. Before an autonomous rule can publish, deterministic code independently re-fetches the authoritative source and confirms the expected source state. An unavailable, blocked, ambiguous, contradictory, or still-open authoritative record fails closed to human review.

## Initial autonomous scope

v0.2.0 intentionally permits one routine autonomous transition:

- record type: `programs`
- record: `P-001`
- field: `status`
- transition: `open` → `closed`
- evidence: `official`
- required canonical source: `S-06`
- confidence: `high`
- contradiction: `false`
- exact canonical old-value match required

Anything outside that rule is human-reviewed or rejected.

## Discovery modes

- **bounded** — scheduled every two hours at minute 17 using only approved monitoring domains. Eligible for deterministic policy evaluation.
- **broad** — scheduled daily for discovery. Any detected change is human-review only.
- **fixture** — on-demand synthetic V&V. Never publishes.
- **repository_dispatch** — optional urgent trigger after activation.

## Source safety

Web pages are evidence inputs, not trusted instructions. Prompt-like text found inside sources must be ignored. Unknown source domains cannot auto-publish.

## Credentials

The workflow expects:

- secret `OPENAI_API_KEY`
- secret `PAX_BOT_PRIVATE_KEY`
- repository variable `PAX_BOT_CLIENT_ID`
- repository variable `PAX_OPENAI_MODEL` (recommended `gpt-5.6-terra`)
- repository variable `PAX_LIVE_INTELLIGENCE_ENABLED`

The workflow is committed disabled by default and should remain disabled until credential installation, synthetic V&V, a live no-change scan, repository rules, and final activation are reviewed.

## Audit evidence

Every scan uploads candidate, deterministic decision, and bounded API metadata. No secrets or raw private data are included. No-change scans do not modify the repository.

Field-level automated verification updates only the records actually reverified. It does not advance the global `snapshot.verified_through` baseline; that baseline moves only after a whole-snapshot review.

Human-review candidates are preserved in a deduplicated review queue keyed by a deterministic candidate fingerprint.

## Human review examples

Human review is required for new members, new source domains, contradictory official records, reported/draft policy, geopolitical interpretation, financing/build/operating/qualification claims, supersession/deletion, new BN7 analysis, or any change that strengthens an evidence state.
