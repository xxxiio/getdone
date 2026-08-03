---
id: acceptance.change-type.bug-fix
version: 1.1.0
status: stable
---
# Bug-Fix Acceptance

## Objective
Reproduce the reported defect and correct its root cause with the smallest safe change.

## Pass conditions
A regression test or deterministic reproduction fails before the fix and passes afterward; affected data, clients, and adjacent cases are assessed.

## Required evidence
Record the task-specific proof above together with the core gate statuses and commands.

## Waiver conditions
Use the core waiver format; name the unavailable primary evidence, alternative evidence, and residual risk.

## Failure conditions
A test that does not reproduce the defect, symptom suppression without root-cause analysis, or unrecorded remediation needs.
