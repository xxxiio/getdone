# Project-agent extensions

A consuming repository may add a `.project-agent/` directory to extend GetDone with
durable project-specific engineering guidance without changing GetDone's generic workflows.

## Ownership boundary

- `.agent/` remains mutable GetDone/project execution state.
- `.project-agent/` is durable repository-owned agent guidance.
- GetDone indexes and selects `.project-agent/` content, but does not interpret project
  concepts such as layers, packages, frameworks, products, or domains.

## Required files

```text
.project-agent/
├── AGENTS.md
└── index.json
```

`AGENTS.md` is the always-loaded project baseline. Keep it small and reserve it for
project invariants that apply to every task.

`index.json` routes changed paths and project-defined concerns to conditional guidance.

## Language selection

`--language` remains repeatable and acts as an explicit addition/override.

When `--changed-path` is supplied, GetDone also infers affected languages from file
extensions. A project-agent index may add project-specific glob patterns for supported
GetDone language IDs.

This means polyglot tasks can normally be invoked as:

```bash
getdone context \
  --task-class feature \
  --project-root . \
  --changed-path packages/core/src/lib.rs \
  --changed-path tooling/build.py
```

Explicit `--language` remains useful for new files or planned changes that do not yet
exist in the diff.

## Project index

Example:

```json
{
  "schema_version": 1,
  "language_patterns": {
    "dart-flutter": ["applications/**/*.dart", "packages/**/*.dart"]
  },
  "infer": [
    {
      "paths": ["applications/**/view/**"],
      "concerns": ["gui"]
    }
  ],
  "rules": [
    {
      "id": "app-gui",
      "paths": ["applications/**"],
      "concerns": ["gui"],
      "load": ["implementation/app/gui.md"]
    }
  ]
}
```

Within one rule, paths are ORed and concerns are ORed. When both groups are present,
both the path group and concern group must match. All matching rules compose.

## Doctor

By default:

```bash
getdone doctor --project-root .
```

warns when `.project-agent/` is absent and deeply validates it when present.

Modes:

```bash
getdone doctor --project-agent auto
getdone doctor --project-agent required
getdone doctor --project-agent off
```

`auto` is the default. `required` makes absence blocking. `off` suppresses the check.

Dedicated inspection:

```bash
getdone project-agent validate --project-root .
getdone project-agent inspect --project-root . \
  --changed-path applications/example/view/page.dart
```

Validation checks the baseline, index structure, referenced files, path containment,
duplicate rule IDs, and unindexed Markdown guidance. It also warns when the always-loaded
baseline grows beyond the bounded-context target.
