---
id: policy.template-upgrades
version: 1.0.0
status: stable
---
# Template Upgrades

## Applies when
A consuming project compares or migrates files generated from `skill/bootstrap/templates/`.

## Required action
1. Run update inspection in dry-run mode.
2. Classify each managed file from provenance as current, missing, unmodified and newer,
   modified, untracked, mismatched, invalid, or ahead.
3. Require separate explicit authorisation for additions and verified-unmodified
   replacements.
4. Never write modified, untracked, mismatched, invalid, or ahead project-owned files.
5. Produce a diff or read-only merge aid for every non-current file.
6. Resolve profile inheritance parent-first and reject unknown parents or cycles.
7. Report every write, skip, residual risk, and required manual action.

## Required evidence
Preserve the dry-run plan, file classifications, authorisation category, applied changes,
and post-migration project validation.

## Exceptions
A human may manually reconcile a modified file. Automated migration still must not replace
that file until its provenance is deliberately re-established.
