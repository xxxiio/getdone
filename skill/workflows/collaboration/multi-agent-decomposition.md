---
id: workflow.collaboration.multi-agent-decomposition
version: 1.1.0
status: stable
parent: workflow.general.deterministic-development
required_outputs:
- work ownership map
- integration order
- handoff records
---

# Multi-Agent Task Decomposition

## Use this when

- Use for parallel work can proceed across independent ownership boundaries.

## Do not use this when

- Do not use for tasks share files, mutable state, or unresolved interfaces that make parallelism unsafe.

## Required inputs

- Primary objective, dependency graph, integration owner, and shared contracts.

## Procedure

1. Partition by stable interface, file ownership, or independent evidence.
2. Assign explicit inputs, outputs, exclusions, and acceptance criteria.
3. Define integration order and conflict policy.
4. Require each agent to return changed paths, evidence, risks, and next action.
5. Integrate centrally and rerun cross-boundary tests.

## Decision points

- Do not parallelise work whose interface is still being discovered.
- One owner decides shared-contract changes.

## Required evidence

- Task map, ownership map, per-agent evidence, and integration results.

## Stop conditions

- Dependencies or file ownership are ambiguous.

## Completion criteria

- Parallel outputs integrate without hidden overlap and the primary gate passes.
