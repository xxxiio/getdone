---
id: workflow.general.execution-planning
version: 1.0.0
status: stable
required_outputs:
- validated execution plan with ordered slices
- dependency and integration order
- first deterministic step
---

# Execution Planning

## Use this when

- An approved milestone spans multiple reviewable iterations.
- Ordering, integration, migration, rollback, or ownership is non-obvious.

## Do not use this when

- The work fits honestly into one deterministic step.
- The project outcome or milestone itself is not yet approved; use project planning.

## Required inputs

- Approved milestone and exit criteria.
- Relevant architecture boundaries, invariants, impacts, dependencies, and constraints.

## Procedure

1. Verify the milestone outcome and exit criteria are approved and measurable.
2. Identify assumptions and unknowns that affect ordering; schedule bounded investigations first.
3. Decompose work into stable, independently reviewable `SLICE-NNN` outcomes.
4. Prefer vertical behaviour slices; use enabling slices only when later work cannot proceed without them.
5. For each slice, define scope, must-not-change behaviour, dependencies, advanced exit criteria, validation tier, and binary acceptance criteria.
6. Check dependency references and remove cycles or unsupported sequencing.
7. Define integration order, rollback or stop conditions, and ownership boundaries.
8. Avoid speculative file, class, or function detail unless required by an approved contract.
9. Present the plan for approval before marking it ready.
10. Emit exactly one first deterministic step linked to the first ready slice.

## ChatGPT delivery

- Explain material decomposition choices and trade-offs conversationally.
- When files cannot be edited directly, return the execution-plan record and next-step record as separately labelled Markdown blocks with target paths.
- Distinguish approved plan content from suggestions awaiting confirmation.

## Decision points

- Stay in discovery mode until the user approves commitment.
- Prefer a bounded investigation over speculative sequencing when a high-impact unknown remains.

## Required evidence

- Every slice advances an approved milestone exit criterion.
- Every slice is independently reviewable and has binary acceptance criteria.
- Dependencies, integration order, stop conditions, and the first step are explicit.

## Stop conditions

- The milestone is not approved or lacks measurable exit criteria.
- A high-impact unknown makes decomposition speculative.
- The proposed first slice cannot be reviewed or validated independently.

## Completion criteria

- The execution plan has stable plan and slice IDs with no dependency cycle.
- Exactly one first slice is ready.
- The next deterministic step references that slice and its milestone criteria.
