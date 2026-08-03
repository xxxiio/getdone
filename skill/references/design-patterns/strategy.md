# Strategy

## Intent

Encapsulate a real algorithm or policy variation behind an explicit interchangeable contract.

## Use when

- Callers select among multiple policies with the same purpose.
- The variation changes independently from orchestration.

## Avoid when

- Only one implementation exists and no external seam requires variation.
- A function parameter or simple callable is clearer.

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

- Policy
- Algorithm
- Substitution

Patterns are decision aids, not architecture quotas.
