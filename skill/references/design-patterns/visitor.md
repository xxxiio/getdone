# Visitor

## Intent

Add operations across a stable heterogeneous structure without distributing each operation across every element type.

## Use when

- The data structure is stable while operations grow independently.
- Double dispatch or exhaustive traversal provides clear ownership.

## Avoid when

- Element types change frequently.
- Pattern matching or ordinary polymorphism is simpler.

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

- Traversal
- Operations
- Heterogeneous data

Patterns are decision aids, not architecture quotas.
