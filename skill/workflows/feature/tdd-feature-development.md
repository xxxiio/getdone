---
id: workflow.feature.tdd
version: 1.2.0
status: stable
parent: workflow.general.deterministic-development
required_outputs:
- failing behavioural evidence
- feature implementation
- evidence manifest
---

# Test-Driven Feature Development

## Use this when

- The task adds observable user, API, command, event, or data behaviour.

## Do not use this when

- The task only preserves behaviour while restructuring; use characterisation-first refactoring.
- The task only explores feasibility; use technical investigation.

## Required inputs

- Behavioural specification with examples.
- Compatibility and configuration expectations.
- The smallest useful vertical slice.

## Procedure

1. Choose the most stable observable boundary for the first test.
2. Add a test that fails because the behaviour is absent, and confirm the failure reason.
3. Implement only the code required for the useful slice.
4. Add coverage for every error, boundary, integration, or platform condition declared in the task acceptance criteria or change-impact record.
5. Refactor without changing the demonstrated behaviour.
6. Update public usage, configuration, and compatibility documentation.

## Decision points

- Prefer an integration or component test when a unit test would lock in internal structure.
- Create an abstraction only for demonstrated variation or a stable external boundary.
- Split the feature when independent behaviour cannot be validated in one iteration.

## Required evidence

- The original failing test and passing result.
- A demonstration of user-visible or API-visible behaviour.
- Compatibility, configuration, and documentation impact.

## Stop conditions

- The requested behaviour cannot be stated observably.
- A required dependency or product decision is unresolved.
- Only scaffolding can be delivered without a useful slice.

## Completion criteria

- A useful slice works at an observable boundary.
- Every declared negative and edge condition passes.
- Incomplete scaffolding is not presented as complete.
