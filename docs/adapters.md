# Agent Adapter Contracts

Adapters connect agent-specific instruction surfaces to the canonical shared repository. They must stay thin: workflows, acceptance rules, and engineering guidance belong in their canonical directories rather than being copied into each adapter.

## Delivery models

- `reference-only`: no project file is installed; the agent receives the project and shared-repository context through the conversation or workspace.
- `bootstrap-managed`: the bootstrap profile already creates the required project file.
- `project-file`: a small agent-specific file is copied into the consuming project after bootstrap.

The machine-readable contract lives in [`skill/adapters/manifest.json`](../skill/adapters/manifest.json) and is validated against [`skill/schemas/adapter-manifest.schema.json`](../skill/schemas/adapter-manifest.schema.json).

## Current adapters

| Agent | Delivery | Project surface |
|---|---|---|
| ChatGPT | Reference-only | Conversation or connected workspace |
| Codex | Bootstrap-managed | `AGENTS.md` |
| Claude Code | Project file | `CLAUDE.md` |
| Cursor | Project file | `.cursor/rules/getdone.mdc` |
| GitHub Copilot | Project file | `.github/copilot-instructions.md` |

## Required behaviour

Every adapter must direct the agent to:

1. Read the consuming project's `AGENTS.md`.
2. Verify `.agent/skills.lock.json` against the shared checkout.
3. Locate the shared repository through `.agent/skills-reference.md`.
4. Read the shared `skill/START-HERE.md`.
5. Select work through `skill/workflow-router.md`.
6. Keep mutable state in the consuming project's `.agent/` directory.
7. Treat shared skills content as read-only unless the task explicitly targets it.
8. Apply relevant acceptance gates before reporting completion.
9. Resolve historical IDs through registry aliases and load organisation overlays only when project instructions explicitly name them.

## Installation

List available adapters:

```bash
getdone-install-adapter \
  --skills-root /path/to/getdone \
  --list
```

Install a project-file adapter:

```bash
getdone-install-adapter \
  --project-root /path/to/project \
  --skills-root /path/to/getdone \
  --adapter cursor
```

The project must be bootstrapped first. Existing adapter files are treated as project-owned and are not overwritten unless `--overwrite` is explicit.

## Contract validation

Repository validation checks:

- Manifest schema conformance.
- Safe relative source and destination paths.
- Existence of guidance and template files.
- Required canonical references.
- Thin guidance size limits.
- Destination collisions.

An adapter must not embed the lock contents, duplicate the deterministic workflow or create another mutable project-state location.

## Reuse discovery compatibility

Every adapter contract references `skill/registry/reuse-catalogue.json`. Agents may read the registry directly or call `getdone-search --json`; both surfaces are agent-neutral and contain no vendor-specific execution instructions. Search remains optional and does not authorise shared-component or pattern adoption. Exact alias resolution and explicitly loaded organisation overlays use the same neutral contract.
