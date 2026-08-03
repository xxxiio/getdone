# Project Bootstrap

Bootstrap sources are rendered into consuming projects and immediately become
project-owned mutable state.

## Profiles

- `minimal`: project context, skills reference, and one next step.
- `standard`: extends `minimal` with commands, tasks, acceptance evidence, journals,
  milestones, reports, tracking, decisions, roadmap, and waivers.

Profiles resolve parent-first; a child overrides a matching parent path. Unknown parents,
cycles, and missing source directories are invalid.

## Controlled records

Project-state templates are governed by `skill/contracts/project-records.md` and the
machine-readable `skill/contracts/project-records.json`. Draft records may retain guided
comments; operational statuses require exact headings, controlled IDs and statuses,
binary criteria, evidence, and valid cross-record references.

## Initialise

```bash
getdone-init \
  --project-root /path/to/project \
  --skills-root /path/to/skill-pack \
  --profile standard
```

Existing files are preserved unless overwrite is explicit.

## Provenance and updates

Generated Markdown records template identity, version, project ownership, and a content
digest. Inspect changes without writing:

```bash
getdone-check-updates --project-root /path/to/project --diff --sections
getdone-migrate --project-root /path/to/project
```

Apply additions and verified-unmodified replacements separately:

```bash
getdone-migrate --project-root /path/to/project --apply-additions
getdone-migrate --project-root /path/to/project --apply-replacements
```

Modified, untracked, mismatched, invalid, or ahead project files are never automatically
replaced. See `skill/policies/template-upgrades.md` and `skill/bootstrap/migrations/`.

Validate filled records without changing them:

```bash
getdone-validate-records --project-root /path/to/project --skills-root /path/to/skill-pack
```
