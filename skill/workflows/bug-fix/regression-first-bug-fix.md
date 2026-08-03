---
id: workflow.bug-fix.regression-first
version: 1.2.0
status: stable
parent: workflow.general.deterministic-development
required_outputs:
- regression evidence
- minimal fix
- evidence manifest
---

# Regression-First Bug Fix

## Use this when

- Existing behaviour violates its contract.

## Do not use this when

- The behaviour is new rather than defective; use feature development.
- Production impact requires immediate containment; start with incident response.

## Required inputs

- Defect report or observed symptom.
- Expected and actual behaviour.
- Reproduction conditions.

## Procedure

1. Reproduce the defect with the smallest reliable case.
2. Add failing regression evidence.
3. Trace the root cause and affected boundaries.
4. Implement the smallest safe correction.
5. Add coverage for every adjacent input, client, persisted-data, or integration boundary named in the task or change-impact record.
6. Run the wider relevant suite and record remediation needs.

## Decision points

- If intermittent, first make the failure observable.
- If persisted data is already wrong, separate code correction from data remediation.
- Keep broader architectural migration separate unless inseparable.

## Required evidence

- Before/after reproduction.
- Root-cause explanation tied to changed code.
- Regression and wider-test results.
- Data, client, and remediation impact.

## Stop conditions

- The defect cannot be reproduced or distinguished from an environment issue.
- The safe correction requires product or data-owner authority not available.
- The proposed fix broadens behaviour beyond the defect contract.

## Completion criteria

- The regression evidence passes.
- The root cause, not only the symptom, is addressed.
- Collateral behaviour and remediation needs are recorded.
