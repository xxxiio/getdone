# Builder

## Intent

Construct a complex value through readable, validated steps while keeping invalid intermediate state controlled.

## Use when

- Construction has many optional values, ordering rules, or validation constraints.
- Tests benefit from clear domain-valid defaults.

## Avoid when

- A constructor or named factory with a few fields is clearer.
- The builder duplicates setters without enforcing meaning.

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

- Construction
- Validation
- Test data

Patterns are decision aids, not architecture quotas.
