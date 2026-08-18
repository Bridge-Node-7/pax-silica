# Credibility Contract

Pax Silica Intelligence is designed to make source quality visible without turning the interface into a citation wall.

## Source precedence

1. Primary government or authoritative institutional source for official status.
2. High-quality independent source for corroboration, chronology, or context.
3. Credible reporting for developments that are not yet established as final public policy.
4. Bridge Node 7 analysis remains explicitly labeled analysis.

## Hard rules

- An `official` claim must resolve to at least one `official` source.
- A `reported_draft` claim must resolve to at least one `reported_draft` source.
- Secondary material may corroborate an official claim but may not silently create official status.
- Reported/draft developments do not lead the hero when a newer reviewed official development is available.
- Unknowns remain unknown.
- Superseded records remain part of history but do not render as active state.
- Time-sensitive records carry `review_by` and fail freshness validation when stale.

## Public UX

Source IDs remain small and optional at the point of use. The Evidence section exposes publisher, title, state, supported claims, evidence note, and source URL.

## Freshness semantics

`verified_through` identifies the reviewed snapshot date. `review_by` identifies the deadline for rechecking a time-sensitive record. Validation uses an explicit `as_of` date, defaulting to the current UTC date. A time-sensitive record fails freshness validation when its `review_by` date is earlier than `as_of`.
