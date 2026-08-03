---
id: acceptance.change-type.release
version: 1.1.0
status: stable
---
# Release Acceptance

## Objective
Produce a reproducible artefact with explicit compatibility and rollback information.

## Pass conditions
Version, changelog, tests, build artefacts, checksums, install/upgrade smoke tests, known limitations, and signing/publishing status are recorded.

## Required evidence
Record the task-specific proof above together with the core gate statuses and commands.

## Waiver conditions
Use the core waiver format; name the unavailable primary evidence, alternative evidence, and residual risk.

## Failure conditions
Unverified artefact, stale metadata, or implied signing/publishing that did not occur.
