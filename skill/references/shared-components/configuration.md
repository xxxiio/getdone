# Configuration Boundary

## Intent

Load, validate, and expose configuration through one explicit boundary rather than scattering environment and file access across domain code.

## Use when

- Multiple modules need the same validated settings.
- Configuration sources or precedence rules must remain consistent.
- Tests need to supply configuration without mutating process-wide state.

## Avoid when

- A program has only one or two immutable constants.
- A wrapper would merely rename direct standard-library access without adding policy.

## Required contract

- Define source precedence and override rules.
- Validate at the boundary and return typed values.
- Keep secret handling and redaction explicit.
- Avoid import-time loading and hidden global mutation.

## Failure and lifecycle questions

- Report the source and invalid field without exposing secrets.
- Distinguish missing, malformed, and unsupported configuration.
- Fail early for required settings and document optional defaults.

## Acceptance evidence

- Source precedence
- Validation and defaults
- Secret redaction
- Reload or immutability policy

## Promotion rule

Promote an implementation into a shared component only when compatible semantics, ownership, and upgrade policy are demonstrated across real consumers. Similar-looking code alone is not sufficient.

See [Shared Component Checklist](component-checklist.md).
