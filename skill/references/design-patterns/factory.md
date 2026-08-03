# Factory

## Intent

Centralise object selection or construction policy when callers should not know concrete creation details.

## Use when

- Construction varies by configuration, environment, or capability.
- Creation requires coordinated dependencies or validation.

## Avoid when

- Direct construction is stable and obvious.
- The factory only forwards arguments to one constructor.

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

- Object creation
- Selection
- Lifecycle

Patterns are decision aids, not architecture quotas.
