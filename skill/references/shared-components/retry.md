# Retry and Backoff Policy

## Intent

Centralise retry classification, bounded backoff, jitter, cancellation, and observability for transient failures.

## Use when

- A remote or concurrent operation has documented transient failure modes.
- Several callers need the same retry budget and telemetry.
- Idempotency and cancellation semantics are understood.

## Avoid when

- The operation is not idempotent and cannot be safely deduplicated.
- The failure is deterministic or indicates invalid input.
- Retries would amplify overload or hide a durable outage.

## Required contract

- Classify retryable failures explicitly.
- Bound attempts, elapsed time, and backoff.
- Respect cancellation and deadlines.
- Expose attempts and final exhaustion through telemetry.

## Failure and lifecycle questions

- Return the final causal error with retry context.
- Avoid nested retry layers with multiplying budgets.
- Coordinate with circuit breakers and server retry hints.

## Acceptance evidence

- Transient success
- Permanent failure
- Budget exhaustion
- Cancellation
- Jitter bounds

## Promotion rule

Promote an implementation into a shared component only when compatible semantics, ownership, and upgrade policy are demonstrated across real consumers. Similar-looking code alone is not sufficient.

See [Shared Component Checklist](component-checklist.md).
