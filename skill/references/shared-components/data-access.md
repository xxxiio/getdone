# Data Access Boundary

## Intent

Isolate persistence protocols, queries, transactions, and mapping from domain decisions.

## Use when

- Domain behaviour should not depend on a database client.
- Multiple storage implementations or tests need a stable port.
- Transaction and consistency rules need one owner.

## Avoid when

- A thin script performs one obvious query with no domain layer.
- A repository abstraction would only mirror every table operation.

## Required contract

- Model operations around domain needs rather than storage tables.
- State transaction and consistency expectations.
- Keep mapping and query performance visible.
- Expose pagination and concurrency semantics explicitly.

## Failure and lifecycle questions

- Translate infrastructure errors without losing causal detail.
- Distinguish absence, conflict, timeout, and corruption.
- Define retry and idempotency at the operation level.

## Acceptance evidence

- Contract tests across implementations
- Transaction boundaries
- Mapping edge cases
- Concurrency conflicts

## Promotion rule

Promote an implementation into a shared component only when compatible semantics, ownership, and upgrade policy are demonstrated across real consumers. Similar-looking code alone is not sufficient.

See [Shared Component Checklist](component-checklist.md).
