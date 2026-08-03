---
id: workflow.general.release-maintenance
version: 1.1.0
status: stable
parent: workflow.general.deterministic-development
required_outputs:
- release artefacts
- compatibility and rollback evidence
- release report
---

# Release and Dependency Maintenance

## Use this when

- Use for preparing a release or changing dependency versions and package metadata.

## Do not use this when

- Do not use for implementing product behaviour unrelated to release mechanics.

## Required inputs

- Target version, compatibility policy, artefact list, and rollback or support expectations.

## Procedure

1. Confirm scope and changelog.
2. Run full required validation and install/upgrade smoke tests.
3. Build artefacts from a clean committed state.
4. Generate checksums and verify metadata.
5. Record signing, publishing, and external CI status accurately.

## Decision points

- Dependency changes also apply the dependency acceptance gate.
- Do not claim signing, publication, or platform validation that did not occur.

## Required evidence

- Commit/tag, artefacts, checksums, commands, compatibility notes, and known limitations.

## Stop conditions

- Working tree is dirty or release metadata disagrees.

## Completion criteria

- Reproducible artefacts verify and release status is accurately reported.
