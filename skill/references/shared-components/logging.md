# Structured Logging

## Intent

Provide consistent structured events, context propagation, and redaction without coupling domain logic to one logging vendor.

## Use when

- Multiple components need consistent fields and correlation identifiers.
- Operational diagnosis depends on machine-readable events.
- Sensitive data must be redacted centrally.

## Avoid when

- A small command-line tool only needs direct user-facing output.
- The wrapper would hide useful standard logging APIs without adding policy.

## Required contract

- Separate diagnostic events from user-facing output.
- Define stable event names and required context.
- Propagate request or trace identifiers explicitly.
- Make redaction rules testable.

## Failure and lifecycle questions

- Logging failures must not silently corrupt business state.
- Backpressure, buffering, and delivery guarantees must be stated.
- Never log credentials or unrestricted payloads by default.

## Acceptance evidence

- Required fields
- Redaction
- Context propagation
- Fallback behaviour

## Promotion rule

Promote an implementation into a shared component only when compatible semantics, ownership, and upgrade policy are demonstrated across real consumers. Similar-looking code alone is not sufficient.

See [Shared Component Checklist](component-checklist.md).
