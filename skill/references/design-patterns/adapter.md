# Adapter

## Intent

Translate an external or incompatible interface into a boundary owned by the consuming system.

## Use when

- An external API or legacy interface should not leak through domain code.
- Several callers need one stable translation boundary.

## Avoid when

- The wrapper merely renames every method one-for-one.
- The external interface is already the intended public contract.

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

- Boundary
- Translation
- Anti-corruption layer

Patterns are decision aids, not architecture quotas.
