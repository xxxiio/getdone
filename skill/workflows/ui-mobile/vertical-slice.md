---
id: workflow.ui-mobile.vertical-slice
version: 1.1.0
status: stable
parent: workflow.general.deterministic-development
required_outputs:
- complete user flow
- accessibility and platform evidence
- evidence manifest
---

# UI and Mobile Vertical Slice

## Use this when

- Use for delivering an end-to-end user interaction across UI and state boundaries.

## Do not use this when

- Do not use for changing isolated domain logic with no user-interface behaviour.

## Required inputs

- User scenario, design states, accessibility needs, supported form factors/platforms.

## Procedure

1. Write a component/widget or integration test for the primary interaction.
2. Implement state, domain call, and visible result as one useful slice.
3. Add loading, empty, error, retry, and cancellation behaviour according to risk.
4. Verify accessibility, responsiveness, localisation, and platform differences.
5. Update screenshots or goldens only with reviewed rationale.

## Decision points

- Keep business decisions outside widgets when independently testable.
- Do not split UI and state into separate incomplete tasks when neither is useful alone.

## Required evidence

- Interaction tests, state-path evidence, accessibility/platform checks, and visual review where applicable.

## Stop conditions

- Required design or platform behaviour is unresolved.

## Completion criteria

- The complete interaction works across required states and platforms.
