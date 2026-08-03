---
id: acceptance.change-type.performance-change
version: 1.1.0
status: stable
---
# Performance-Change Acceptance

## Objective
Improve a measured bottleneck without weakening correctness.

## Pass conditions
A reproducible baseline, representative workload, target, before/after result, variance, and regression guard are recorded.

## Required evidence
Record the task-specific proof above together with the core gate statuses and commands.

## Waiver conditions
Use the core waiver format; name the unavailable primary evidence, alternative evidence, and residual risk.

## Failure conditions
Microbenchmark-only claim, changed semantics, or optimisation without measured bottleneck.
