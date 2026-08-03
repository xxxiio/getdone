---
id: acceptance.change-type.execution-planning
version: 1.1.0
status: stable
---
# Execution Planning Acceptance

## Objective
Produce a dependency-aware sequence of independently reviewable slices for one approved milestone.

## Pass conditions
Every slice advances an approved exit criterion, dependencies are acyclic, validation is explicit, and exactly one first slice is ready.

## Required evidence
Record approved decisions, controlled plan records, referenced criteria, dependency checks, and the first deterministic step.

## Waiver conditions
Use the core waiver format; name the unavailable primary evidence, alternative evidence, and residual risk to reviewability or sequencing safety.

## Failure conditions
Slices are speculative, cyclic, untestable, unrelated to milestone criteria, or leave multiple possible first steps.
