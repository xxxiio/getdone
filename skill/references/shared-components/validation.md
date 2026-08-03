# Validation Boundary

## Intent

Convert untrusted or weakly typed input into validated domain values at system boundaries.

## Use when

- The same input rules apply across multiple entry points.
- Domain code should operate on already-valid values.
- Errors need stable machine-readable structure.

## Avoid when

- The validation is a single local invariant already enforced by the type system.
- A shared validator would couple unrelated domain concepts.

## Required contract

- Separate syntactic parsing from domain validation.
- Return all useful errors when safe and actionable.
- Preserve field paths and stable error codes.
- Keep normalisation rules explicit.

## Failure and lifecycle questions

- Reject ambiguous or lossy coercion unless specified.
- Do not expose internal implementation details.
- Differentiate invalid input from unavailable dependencies.

## Acceptance evidence

- Valid values
- Boundary values
- Multiple errors
- Normalisation
- Stable error codes

## Promotion rule

Promote an implementation into a shared component only when compatible semantics, ownership, and upgrade policy are demonstrated across real consumers. Similar-looking code alone is not sufficient.

See [Shared Component Checklist](component-checklist.md).
