---
id: workflow.architecture.design
version: 1.1.0
status: stable
parent: workflow.general.deterministic-development
required_outputs:
- decision record
- boundary and invariant updates
- validation evidence
---

# Architecture Design

## Use this when

- Use for choosing durable component, protocol, data, or deployment boundaries.

## Do not use this when

- Do not use for a local implementation choice with no durable boundary impact.

## Required inputs

- Decision context and quality attributes.
- Current constraints and compatibility obligations.

## Procedure

1. Describe the current state and forces.
2. Define evaluation criteria before options.
3. Compare at least two viable options, including continued current design when viable.
4. Prototype the riskiest assumption only when evidence is missing.
5. Record an ADR with decision, consequences, rollout, ownership, and reversal.

## Decision points

- Choose the simplest option meeting explicit criteria.
- Separate irreversible decisions from choices that can be deferred.

## Required evidence

- ADR, option comparison, and risk evidence.

## Stop conditions

- No decision owner or acceptance criteria.

## Completion criteria

- A decision is recorded and the first implementation slice is bounded.
