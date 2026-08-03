# Pinned Skills Composition

A consuming project stores its resolved shared-guidance set in `.agent/skills.lock.json`. The lock is project-local state; it does not copy workflow text into the project.

## What is pinned

- Core skills release and a digest of canonical guidance.
- Bootstrap profile name, version, lineage, and template digest.
- Adapter contract version and digest.
- Explicit organisation overlays, including referenced Markdown.
- One composition digest over the complete set.

This lets ChatGPT and coding agents verify that they are reading the same guidance without loading every document into context.

## Bootstrap

`getdone-init` creates the lock automatically. Pin overlays at the same time when the project uses them:

```bash
getdone-init \
  --project-root /work/example \
  --skills-root /opt/getdone \
  --profile standard \
  --overlay /work/example/agent-guidance/registry-overlay.json
```

## Check and update

Strict check against the available checkout and locked overlays:

```bash
getdone-lock \
  --project-root /work/example \
  --skills-root /opt/getdone
```

Review a newer checkout without writing:

```bash
getdone-lock \
  --project-root /work/example \
  --skills-root /opt/getdone-next \
  --plan
```

Update only after reviewing the classified component changes:

```bash
getdone-lock \
  --project-root /work/example \
  --skills-root /opt/getdone-next \
  --write
```

`--write` replaces only the lockfile. It does not migrate project templates or modify project-owned Markdown.

## Classification

- `current`: digest and version match.
- `compatible-update`: a higher minor or patch version changed content.
- `breaking-update`: the major version changed.
- `drift`: content changed without a version change.
- `missing`, `added`, or `downgrade`: composition review is required.

Project validation is strict: the resolved composition must be `current`.

## Context efficiency

The lock is a verification index, not a prompt bundle. After verification, load only:

1. The workflow selected by `skill/workflow-router.md`.
2. The applicable language and change-type practices.
3. The acceptance gates needed for the current change.
4. Exact catalogue entries discovered for a concrete design decision.

Do not preload the complete repository or duplicate canonical guidance into adapters, plans, or prompts.
