---
id: acceptance.change-type.database-change
version: 1.1.0
status: stable
---
# Database-Change Acceptance

## Objective
Change persisted schemas or data without losing correctness or recoverability.

## Pass conditions
Forward and rollback/recovery procedures are tested; compatibility window, backfill/restart behaviour, observability, and representative data checks are recorded.

## Required evidence
Record the task-specific proof above together with the core gate statuses and commands.

## Waiver conditions
Use the core waiver format; name the unavailable primary evidence, alternative evidence, and residual risk.

## Failure conditions
Non-restartable migration, silent truncation, unbounded lock risk, or no recovery path.
