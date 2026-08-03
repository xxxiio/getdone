---
id: workflow.refactoring.characterisation-first
version: 1.2.0
status: stable
parent: workflow.general.deterministic-development
required_outputs:
- characterisation evidence
- behaviour-preserving refactor
- evidence manifest
---

# Characterisation-First Refactoring

## Use this when

- The objective is structural improvement while authorised behaviour remains stable.

## Do not use this when

- The task intentionally changes observable behaviour; separate it as a feature or bug fix.

## Required inputs

- The structural problem and measurable improvement.
- Behaviour and public contracts that must remain unchanged.
- Existing tests and coverage gaps.

## Procedure

1. Establish a passing baseline.
2. Add characterisation tests where current behaviour is not adequately protected.
3. Choose a small reversible structural step.
4. Refactor and run focused tests after each step.
5. Run the wider relevant suite.
6. Demonstrate the claimed structural improvement.

## Decision points

- Stop when a proposed split leaves components that must change together or adds indirection without isolating an independent responsibility.
- Preserve public contracts unless a separate authorised change says otherwise.
- Avoid speculative interfaces without a real seam.

## Required evidence

- Baseline and characterisation results.
- Behaviour-preservation evidence.
- Before/after structural evidence.
- Remaining limitations.

## Stop conditions

- A stable baseline cannot be established.
- Required behaviour is unknown and cannot be characterised safely.
- The refactor requires an unapproved public-contract change.

## Completion criteria

- Protected behaviour is unchanged.
- The stated structural problem is measurably or observably improved.
- No unrelated behavioural change is bundled.
