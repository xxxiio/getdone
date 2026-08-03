# Worked Example: Explicit Job Lifecycle

## Problem

A background job used several booleans for running, cancelled, failed, and completed. Invalid combinations appeared after concurrent cancellation.

## Decision

Represent lifecycle as an enum and define allowed event-driven transitions with guards. Transition functions are pure; side effects execute only after a valid transition is accepted.

## Rejected alternatives

- More boolean checks increased the number of invalid combinations.
- A workflow framework was unnecessary for six states and a small event set.

## Acceptance evidence

A transition-table test covers every state and event, including duplicate completion, cancellation races, and terminal-state immutability.
