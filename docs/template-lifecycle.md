# Project Template Lifecycle

## Ownership model

Bootstrap templates are shared source material. Files generated into a consuming project are project-owned from the moment they are created.

A template update therefore produces a migration plan and requires explicit authorisation before any safe write.

## Provenance

Every managed Markdown template has front matter containing:

- `template`: stable template identity
- `template_version`: semantic version of that template
- `project_owned: true`: explicit ownership transfer
- `template_digest`: digest of the exact generated content before project edits

The shared-skills reference also records the selected profile, profile version, and resolved inheritance lineage.

## Profile inheritance

Profiles resolve parent-first. A child profile receives all parent files and may override a parent file at the same relative path. Unknown parents and cycles are rejected. See [`profile-inheritance.md`](profile-inheritance.md).

## Checking for updates

Run:

```bash
getdone-check-updates \
  --project-root /path/to/consuming-project \
  --diff
```

The checker is read-only. It reports:

| Status | Meaning | Automatic action allowed |
|---|---|---|
| `current` | Installed version matches and content is unmodified | None required |
| `missing` | A resolved profile template is absent | Safe addition after explicit authorisation |
| `update-available` | A newer template exists and installed content is unmodified | Safe replacement after explicit authorisation |
| `modified` | Project content differs from its generated digest | Never overwrite automatically |
| `untracked` | File predates provenance metadata | Review and migrate manually |
| `template-mismatch` | Template identity changed unexpectedly | Investigate |
| `ahead` | Project version is newer than the shared source | Investigate source selection |
| `invalid-version` | A template version is not semantic | Correct metadata |
| `unmanaged-source` | Shared source lacks required provenance | Fix the skills repository |

## Applying safe migrations

The migration command is a dry run unless a write category is explicitly authorised:

```bash
getdone-migrate --project-root /path/to/consuming-project
```

Apply missing files only:

```bash
getdone-migrate \
  --project-root /path/to/consuming-project \
  --apply-additions
```

Apply newer verified-unmodified templates only:

```bash
getdone-migrate \
  --project-root /path/to/consuming-project \
  --apply-replacements
```

The two flags may be combined after reviewing the plan. Modified, untracked, mismatched, invalid, or ahead files remain untouched.

Use `--profile <name>` to plan or perform a profile migration. Safe additions should be applied first. The migration tool defers profile-reference replacement while required additions remain pending, so an incomplete project does not claim the target profile.

## Migration policy

1. Add missing files only when they do not conflict with project conventions.
2. Replace an unmodified file only through the replacement authorisation.
3. Never replace a locally modified file automatically.
4. Produce a unified diff for every non-current managed file.
5. Preserve project IDs, decisions, status, and historical records.
6. Record breaking template changes under `skill/bootstrap/migrations/`.
7. Keep additions and replacements as separately reviewable write categories.
8. Update profile metadata only through an accepted managed-template replacement.

## Template versioning

Increment a template version when its generated structure or required semantics change:

- Patch: wording or non-structural clarification.
- Minor: additive sections or backward-compatible metadata.
- Major: renamed or removed sections, changed ownership semantics, or a richer profile override replacing a parent form.

Increment a profile version when its effective file set, inheritance graph, overlay order, or required semantics change. Repository, profile, and template versions are related but independent.
