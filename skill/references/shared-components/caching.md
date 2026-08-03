# Caching Boundary

## Intent

Make cache keys, freshness, invalidation, ownership, and failure behaviour explicit at a stable boundary.

## Use when

- Repeated reads are expensive and staleness is acceptable.
- Cache identity and invalidation rules can be defined precisely.
- The system can measure hit rate and stale data risk.

## Avoid when

- Correctness requires immediately current state.
- No evidence shows repeated work is a bottleneck.
- Invalidation ownership is unclear.

## Required contract

- Define key normalisation and namespace ownership.
- State TTL, refresh, eviction, and invalidation semantics.
- Make cache bypass and observability available.
- Treat caches as disposable unless explicitly durable.

## Failure and lifecycle questions

- Specify fail-open or fail-closed behaviour.
- Prevent stampedes where concurrent misses are likely.
- Do not let cache errors masquerade as authoritative absence.

## Acceptance evidence

- Hit and miss
- Expiry
- Invalidation
- Concurrent fill
- Backend outage

## Promotion rule

Promote an implementation into a shared component only when compatible semantics, ownership, and upgrade policy are demonstrated across real consumers. Similar-looking code alone is not sufficient.

See [Shared Component Checklist](component-checklist.md).
