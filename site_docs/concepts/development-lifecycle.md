---
title: "Development lifecycle"
description: "How workflows, standards, acceptance gates, and project records compose."
tags: ["concepts", "workflow"]
---

# Development lifecycle

A normal iteration follows one deterministic composition:

1. Read project context and the current next step.
2. Classify the task and change impact.
3. Select one primary workflow.
4. Load the core standard, every language standard materially affected by the task, core acceptance, and the relevant change-type acceptance gate. Do not load a language standard merely because that language exists elsewhere in the repository.
5. Implement the smallest coherent slice.
6. Run the required test tier and project-defined commands.
7. Record evidence, update current state, and define exactly one next deterministic step.

## Guidance versus state

- `skill/` contains shared, read-only guidance.
- `.agent/` contains mutable project-owned records.
- Workflow definitions prescribe procedure.
- Standards define implementation quality.
- Acceptance gates define what must be proven.
- Evidence records prove what actually happened.

## Conditional loading

Policies, specialist workflows, references, and record contracts are loaded only when a trigger applies. This preserves accuracy without paying the token cost of the whole repository on every task.


## Polyglot changes

A task may affect one or several implementation languages. Select a language standard when the task modifies that language, changes an interface consumed by it, changes generated bindings or shared schemas, or requires validation implemented in it.

Repeat `--language` for cross-language work:

```bash
getdone context \
  --skills-root /path/to/getdone-skill-pack \
  --task-class feature \
  --language python \
  --language rust \
  --language q-kdbplus
```

The base workflow, core standard, core acceptance gate, and change-type gate are loaded once. Each materially affected language contributes one additional language standard.
