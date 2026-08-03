---
id: workflow.database.schema-change
version: 1.1.0
status: stable
parent: workflow.general.deterministic-development
required_outputs:
- schema migration
- rollback and restartability evidence
- compatibility assessment
---

# Database and Schema Change

## Use this when

- Use for changing persisted schema, keys, indexes, stored data, or compatibility contracts.

## Do not use this when

- Do not use for an in-memory model change with no persisted compatibility effect.

## Required inputs

- Current and target schemas.
- Data volume, compatibility window, ownership, and recovery requirements.

## Procedure

1. Choose expand/migrate/contract or another restartable sequence.
2. Add compatibility tests before migration.
3. Test migration and recovery on representative data.
4. Instrument progress, failures, and data-quality checks.
5. Run the bounded stage and verify readers/writers.
6. Remove compatibility only after all consumers are verified.

## Decision points

- Prefer idempotent and resumable operations.
- Separate schema deployment from large backfills when operational risk differs.

## Required evidence

- Migration/recovery commands, representative results, compatibility checks, and observability.

## Stop conditions

- No recovery path, unbounded lock risk, or unknown data owner.

## Completion criteria

- The stage is restartable, compatible, observable, and data checks pass.
