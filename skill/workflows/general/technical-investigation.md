---
id: workflow.general.technical-investigation
version: 1.1.0
status: stable
parent: workflow.general.deterministic-development
required_outputs:
- bounded findings
- decision or no-change outcome
- recommended next step
---

# Technical Investigation

## Use this when

- A bounded unknown, feasibility question, root-cause hypothesis, or design comparison must be resolved.

## Do not use this when

- The required behaviour and implementation path are already known.

## Required inputs

- One decision or unknown.
- Evidence threshold and time or scope boundary.
- Relevant environment, data, and constraints.

## Procedure

1. State hypotheses and the evidence that would support or reject each one.
2. Design the smallest reproducible experiment or source inspection.
3. Record commands, environment, inputs, outputs, and limitations.
4. Separate observations from inferences.
5. Compare options against explicit criteria.
6. Conclude with a supported decision, rejected option, bounded next experiment, or unresolved blocker.

## Decision points

- Use a prototype only when it is the cheapest evidence; do not silently turn it into production code.
- Stop when the evidence threshold is met, not when every adjacent question is answered.

## Required evidence

- Reproducible experiment or cited source evidence.
- Findings, inferences, limitations, and recommendation.
- Disposition of prototype artefacts.

## Stop conditions

- The question is unbounded or has no decision owner.
- Required data or environment is unavailable.
- Further work would be production implementation rather than investigation.

## Completion criteria

- The original unknown has a supported disposition.
- Evidence and limitations can be reviewed independently.
- Production work, if any, is a separate deterministic task.
