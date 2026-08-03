# Worked Example: Typed Configuration Boundary

## Problem

A service read environment variables throughout the codebase. Defaults differed by module and tests mutated global process state.

## Decision

Load environment and file values once at the composition root, validate them into an immutable settings value, redact secrets in diagnostics, and inject the settings or smaller derived values into components.

## Rejected alternatives

- A global singleton preserved hidden dependencies and test interference.
- Passing the raw environment mapping allowed every module to invent parsing rules.

## Acceptance evidence

Tests cover precedence, missing required values, invalid durations, redaction, and deterministic construction without process mutation.
