# Worked Example: Bounded Retry Policy

## Problem

Several HTTP callers retried every exception independently. Nested retries multiplied traffic during outages and cancellation was ignored.

## Decision

Introduce one retry policy at the outbound transport boundary. It classifies documented transient responses, honours the caller deadline, applies bounded exponential backoff with jitter, and emits one event per attempt.

## Rejected alternatives

- Retrying inside each domain service duplicated policy and created nested budgets.
- Retrying every exception would repeat invalid requests and programming failures.
- An unbounded generic decorator hid idempotency and cancellation requirements.

## Acceptance evidence

Tests cover transient success, permanent failure, deadline cancellation, maximum elapsed time, and server-provided retry hints. Metrics expose attempts, exhaustion, and total delay.
