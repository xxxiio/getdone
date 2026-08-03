---
id: acceptance.change-type.dependency-change
version: 1.1.0
status: stable
---
# Dependency-Change Acceptance

## Objective
Introduce or update a dependency only when its value exceeds lifecycle and security cost.

## Pass conditions
Need, alternatives, version constraints, licence/security review, lockfile, compatibility, and removal path are recorded; build and package tests pass.

## Required evidence
Record the task-specific proof above together with the core gate statuses and commands.

## Waiver conditions
Use the core waiver format; name the unavailable primary evidence, alternative evidence, and residual risk.

## Failure conditions
Dependency added for trivial code, hidden transitive reliance, or unsupported runtime impact.
