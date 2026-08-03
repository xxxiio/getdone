# Testing Utilities

## Intent

Share deterministic fixtures, fakes, builders, clocks, and assertions that encode stable testing semantics rather than incidental implementation.

## Use when

- Several test suites need the same domain-valid setup.
- Time, identifiers, or external boundaries need deterministic control.
- A helper reduces duplication without hiding important test intent.

## Avoid when

- A helper makes tests read like a private programming language.
- It couples tests to internal structure or broad mutable fixtures.
- Only one test needs the behaviour.

## Required contract

- Prefer small composable builders and explicit defaults.
- Make randomness and time injectable.
- Keep failures readable at the call site.
- Version shared fixtures when their meaning changes.

## Failure and lifecycle questions

- Do not swallow assertion context.
- Avoid global fixture mutation and order dependence.
- Keep production-only behaviour out of test helpers.

## Acceptance evidence

- Determinism
- Readable failures
- Isolation
- Builder validity
- Compatibility with production contracts

## Promotion rule

Promote an implementation into a shared component only when compatible semantics, ownership, and upgrade policy are demonstrated across real consumers. Similar-looking code alone is not sufficient.

See [Shared Component Checklist](component-checklist.md).
