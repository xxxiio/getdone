---
id: policy.destructive-actions
version: 1.0.0
status: stable
---
# Destructive Actions

## Applies when
An action may delete, overwrite, irreversibly migrate, or make difficult-to-recover
changes to repositories, branches, persistent data, environments, user content, or
project-owned state.

## Required action
1. Name the exact target and expected effect.
2. Prefer a dry run, backup, reversible operation, or narrower scope.
3. Obtain explicit authorisation for the destructive action immediately before it.
4. Verify the target has not changed since authorisation.
5. Run the smallest authorised operation and report the outcome.

## Required evidence
Record the target, authorisation, recovery mechanism, command or operation, and result.

## Exceptions
Routine replacement of reproducible build output is allowed only when the project
explicitly classifies it as disposable. Ambiguity is not authorisation.
