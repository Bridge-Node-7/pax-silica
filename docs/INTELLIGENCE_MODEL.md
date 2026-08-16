# Intelligence Model

Pax Silica Intelligence separates three public layers:

1. **Reference** — durable facts, entities, programs, policy instruments, and sources.
2. **Change Intelligence** — time-stamped events and state transitions.
3. **BN7 Analysis** — original Bridge Node 7 interpretation, frameworks, and hypotheses.

The public site is a deterministic view of reviewed records. It is not the canonical store of facts.

## Source → Claim → Display

Sources and claims are separate records. A display may reuse a reviewed claim without independently paraphrasing the source again.

## Evidence state

- `official`
- `secondary`
- `reported_draft`
- `bn7_analysis`
- `unknown`
- `superseded`

## Workflow state

- `candidate`
- `reviewed`
- `approved`
- `published`
- `retired`

Evidence state and workflow state answer different questions and must not be conflated.

## Derived values

Counts and summary metrics are derived from canonical records. Do not hand-maintain a signatory count, regional count, source count, or award summary in HTML or JavaScript.
