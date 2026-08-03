---
id: workflow.architecture.migration
version: 1.1.0
status: stable
parent: workflow.general.deterministic-development
required_outputs:
- migration plan
- compatibility and rollback evidence
- updated next step
---

# Architecture Migration

## Use this when

- Use for moving from one architecture state to another while serving existing users.

## Do not use this when

- Do not use for a single local refactor with no compatibility window.

## Required inputs

- Current and target states.
- Compatibility, rollback, and data constraints.

## Procedure

1. Define stages with observable entry and exit criteria.
2. Introduce compatibility seams before moving callers or data.
3. Migrate one bounded slice and verify both old and new paths.
4. Measure progress and operational signals.
5. Remove the old path only after consumers and recovery conditions are verified.

## Decision points

- Prefer reversible dual-run or expand/migrate/contract sequencing.
- Do not combine migration and cleanup when rollback still depends on the old path.

## Required evidence

- Stage results, compatibility tests, migration progress, and rollback evidence.

## Stop conditions

- No safe compatibility or recovery path exists.

## Completion criteria

- The current stage is complete; remaining stages are explicit and no premature removal occurred.
