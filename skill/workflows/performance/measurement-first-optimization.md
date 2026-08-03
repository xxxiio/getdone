---
id: workflow.performance.measurement-first
version: 1.1.0
status: stable
parent: workflow.general.deterministic-development
required_outputs:
- baseline measurement
- optimized implementation
- performance regression evidence
---

# Measurement-First Performance Optimisation

## Use this when

- Use for a measured workload misses a defined latency, throughput, memory, or cost target.

## Do not use this when

- Do not use for performance is assumed but not measured.

## Required inputs

- Representative workload, environment, metric, baseline, target, and correctness constraints.

## Procedure

1. Create a reproducible benchmark.
2. Profile and identify the dominant bottleneck.
3. Change one bounded cause.
4. Compare before/after with variance and correctness checks.
5. Add a regression threshold appropriate to measurement stability.

## Decision points

- Reject improvements caused by changed semantics or unrealistic data.
- Prefer algorithmic and I/O improvements before micro-optimisation.

## Required evidence

- Benchmark definition, profile evidence, before/after results, variance, and guard.

## Stop conditions

- No representative workload or measurable target.

## Completion criteria

- Target improvement is demonstrated without correctness regression.
