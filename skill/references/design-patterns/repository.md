# Repository

## Intent

Expose persistence operations in domain terms while isolating storage protocols and mapping.

## Use when

- Domain logic needs a stable persistence port.
- Storage implementations or test substitutes vary.

## Avoid when

- The abstraction mirrors tables or generic CRUD without domain meaning.
- A one-off data script has no durable domain boundary.

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

- Persistence
- Domain boundary
- Transactions

Patterns are decision aids, not architecture quotas.
