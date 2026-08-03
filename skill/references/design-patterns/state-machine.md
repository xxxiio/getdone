# State Machine

## Intent

Model allowed states, events, guards, and transitions explicitly when lifecycle behaviour is non-trivial.

## Use when

- Illegal transitions must be prevented and explained.
- Concurrent or long-lived workflows have observable lifecycle states.

## Avoid when

- There are only two obvious states with no transition rules.
- A large framework obscures a small enum and match statement.

## Decision questions

- What concrete source of variation, lifecycle, or ownership does the pattern make explicit?
- Could a function, value object, enum, or direct dependency remain clearer?
- Does the pattern reduce the cost of testing and future change after its extra concepts are counted?
- Are public contracts and failure behaviour smaller and clearer than before?

## Evidence before adoption

- Name at least two real callers, implementations, operations, or transitions when the pattern depends on variation.
- Show the boundary in tests or a small worked example.
- Record why simpler alternatives were rejected when the added indirection is material.

## Tags

- Lifecycle
- Transitions
- Concurrency

Patterns are decision aids, not architecture quotas.
