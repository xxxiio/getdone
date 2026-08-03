# Audit Event Envelope

Use a stable organisation-owned envelope for security and compliance events that must cross service boundaries.

## Contract

- Preserve actor, action, target, outcome, correlation identifier, source system, and event time.
- Version the payload explicitly.
- Keep sensitive values out of free-text fields.
- Define ownership and retention with the organisation's compliance team.

## Avoid when

Do not replace domain events or general application logging with the audit envelope.
