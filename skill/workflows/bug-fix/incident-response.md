---
id: workflow.bug-fix.incident-response
version: 1.1.0
status: stable
parent: workflow.general.deterministic-development
required_outputs:
- incident evidence
- containment and recovery report
- durable follow-up task
---

# Incident Response

## Use this when

- Use for active production impact requires containment and restoration.

## Do not use this when

- Do not use for a non-urgent defect with no active operational impact.

## Required inputs

- Impact, affected users, timeline, and available telemetry.
- Authority for mitigation and rollback.

## Procedure

1. Declare scope and preserve evidence.
2. Contain impact with the lowest-risk reversible action.
3. Verify service restoration and monitor recurrence.
4. Record timeline, decisions, and communications.
5. Create a regression-first repair task and post-incident follow-ups.

## Decision points

- Prioritise safety and restoration over code elegance.
- Keep mitigation separate from durable repair when possible.

## Required evidence

- Impact timeline, mitigation command/change, restoration metrics, and follow-up owners.

## Stop conditions

- Mitigation is destructive or exceeds authority.

## Completion criteria

- Impact is contained, restoration is verified, and durable repair is tracked.
