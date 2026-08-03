# Measured Context Selection

## Decision

`getdone-select-context` returns canonical product paths and an integrity digest for
feature, bug-fix, refactoring, and investigation tasks. It does not infer task intent,
concatenate documents, or generate prompt text.

Run it only after project startup, composition verification, and explicit task
classification.

## Current recurring set

A normal feature, bug-fix, or refactoring task loads six documents:

1. General deterministic workflow.
2. Task-specific workflow.
3. Core engineering standard.
4. Language standards for every materially affected implementation surface.
5. Core acceptance gate.
6. Applicable change-type gate.

An investigation normally loads five because it has no separate change-type gate.
Policies and registry references remain conditional.

## Benchmark method

Eight committed cases cover the four selected task classes and all five language
families. Measurements include route accuracy, required-document recall, missed gates,
document count, and approximate tokens at four characters per token.

The full baseline is every Markdown document in `skill/`. This is deliberately a static
routing benchmark; executable coding outcomes are covered by the rollout matrix.

## Current result

- Cases: 9
- Full product baseline: 134 Markdown documents, approximately 45,257 tokens
- Maximum selected documents: 6
- Average selected context: approximately 3,829 tokens
- Route accuracy: 100%
- Required-document recall: 100%
- Missed acceptance gates: 0
- Average reduction against full product: 91.54%
- Minimum reduction against full product: 91.27%
- Reduction against RC.1 selected context: 21.16%

RC.1 selected 17 documents and approximately 4,856 tokens on average. The current routed
set remains smaller while making workflows, standards, gates, and policies more operational.

The fixture and published result live under `development/benchmarks/context-selection/`. Repository
validation fails when the report drifts from product content or selector behaviour.
