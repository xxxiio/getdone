# Skill Authoring and Lifecycle

Use `skill/workflows/governance/skill-authoring-lifecycle.md` for any change that adds, promotes, deprecates, replaces, or retires reusable guidance.

## Contribution sequence

1. Start from `templates/governance/skill-proposal.md`.
2. Search the current registry for overlap.
3. Author canonical Markdown and schema-backed metadata.
4. Add failing validation or behaviour tests first where practical.
5. Run `python development/scripts/generate_indexes.py --write`.
6. Complete `templates/governance/registry-change-review.md` during review.
7. Apply `acceptance/change-types/skill-registry-change.md`.

## Lifecycle metadata

Every workflow and reuse entry records:

- stable canonical ID;
- zero or more historical aliases;
- introduction version;
- lifecycle status;
- optional deprecation version and replacement.

Aliases are compatibility references, not alternate names to add casually. Search may match them, and exact `--id` resolution reports which alias was used.

## Exact resolution

```bash
getdone-search \
  --repository-root /path/to/getdone \
  --id workflow.feature.test-driven-development \
  --json
```

Exact resolution includes lifecycle metadata even for deprecated or retired entries. Default ranked discovery excludes draft and retired entries.

## Generated indexes

Check index drift:

```bash
python development/scripts/generate_indexes.py \
  --repository-root /path/to/getdone
```

Regenerate after an approved registry change:

```bash
python development/scripts/generate_indexes.py \
  --repository-root /path/to/getdone \
  --write
```
