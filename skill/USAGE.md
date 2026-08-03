---
id: guide.usage
version: 1.0.0
status: stable
---

# How to Use This Skill Repository

## Purpose

Use this repository as a versioned, read-only development skill pack plus small project-owned records. Do not copy the complete repository into every project and do not load every skill document for every task.

## Agent and CLI responsibilities

During normal development, the agent primarily works from:

- the consuming project's `.agent/` records; and
- the small set of read-only `skill/` documents selected for the current task.

The `getdone` CLI supports that work by bootstrapping project records, selecting guidance,
validating contracts and evidence, diagnosing configuration, and generating planning
prompts. It does not replace the records or act as the project's source of truth.

A coding agent with shell access should use both surfaces: read and update the files, then
run the relevant `getdone` validation commands. A conversational agent without shell or
repository access should produce complete proposed record files for the user to apply; it
must not claim those files were written or validated locally.

## Install the tooling

Install the released wheel or use a trusted checkout:

```bash
python -m pip install getdone_dev-<version>-py3-none-any.whl
```

Keep the product-only skill pack at a stable local path or internal distribution URL.

## Bootstrap a project

Use the minimal profile for small projects and the standard profile for projects that need controlled planning, evidence, decisions, risks, and handoffs:

```bash
getdone-init \
  --project-root /path/to/project \
  --skills-root /path/to/skill-pack \
  --profile standard
```

Bootstrap files under `.agent/` are project-owned. Edit those records in the project; do not edit shared `skill/` content to record project state.

## Start a task

1. Verify the composition lock.
2. Select one primary workflow and the language standards for every materially affected implementation surface.
3. Update `.agent/current/task.md` with one bounded objective and binary acceptance criteria.
4. Complete `.agent/current/change-impact.md`; use only `yes`, `no`, or `unknown` and activate every required specialist gate.
5. Confirm the next step advances an active roadmap exit criterion.
6. Load only the selected workflow, core standard, affected language standards, core acceptance, and applicable change gate.


Select a language because the task materially affects that implementation surface, not merely because the repository contains it. Material impact includes changed source files, public or FFI boundaries, shared schemas or generated bindings, packaging or deployment behaviour, and tests required in that language. Repeat `--language` for polyglot changes.

Example context selection:

```bash
getdone-select-context \
  --repository-root /path/to/skill-pack \
  --task-class feature \
  --language python \
  --language rust
```

## Implement and validate

Follow the selected workflow and the project command reference. Use the declared test tier:

- Tier 1: changed unit tests.
- Tier 2: affected module or package tests.
- Tier 3: relevant integration and contract tests.
- Tier 4: canonical full repository health gate.

Increase the tier for public APIs, persistence, dependencies, concurrency, security, deployment, or other broad impacts. Do not describe a check as passed unless the exact evidence is recorded.

## Finish a task

1. Fill `.agent/current/evidence.md` from actual commands and artefacts.
2. Evaluate acceptance gates and record skipped checks, waivers, and residual risks.
3. Update affected project records only; do not rewrite the roadmap after every task.
4. Preserve or update active invariants in `.agent/invariants.md`.
5. Create the completion or handoff report required by the workflow.
6. Define exactly one next deterministic step, or record a justified no-change outcome.
7. Validate project records:

```bash
getdone-validate-project \
  --project-root /path/to/project \
  --skills-root /path/to/skill-pack
```

Use the umbrella CLI when a concise, read-only operational report is needed:

```bash
getdone status \
  --project-root /path/to/project \
  --skills-root /path/to/skill-pack
```

The report summarizes the current milestone, task, next step, acceptance, evidence, and
record-consistency findings. It does not create or update project records.

## Project record authority

When project records disagree, use this order unless a more specific project policy overrides it:

1. Current user instruction.
2. Accepted policy or architecture decision.
3. Active milestone scope and exit criteria.
4. Current task scope and acceptance criteria.
5. Current next deterministic step.
6. Current project status.
7. Roadmap ordering.
8. Journal entries and historical reports.

By subject, the authoritative records are:

- Commands: `.agent/command-reference.md`.
- Stable project constraints: `.agent/project-context.md` and accepted decisions.
- Current objective: `.agent/current/task.md`.
- Impact and activated gates: `.agent/current/change-impact.md`.
- Acceptance claims: `.agent/current/evidence.md` and `.agent/current/acceptance.md`.
- Critical truths to preserve: `.agent/invariants.md`.
- History: journal and completed reports.

Historical records never override current approved state.

## Maintain the skill repository

Treat changes to shared workflows, standards, contracts, schemas, templates, registries, or tooling as product changes. Update tests, migration guidance, context benchmarks, rollout evidence, version metadata, and public contracts together. Prefer adding enforceable registry or validation behaviour over adding another always-loaded prose document.

## Planning a project

Use `project-planning` when outcomes, MVP scope, or milestone order are still being discussed. Use `execution-planning` only after a milestone is approved and needs multiple reviewable slices. For ChatGPT, print a canonical prompt with `getdone planning-prompt --mode project` or `--mode execution`. Discussion remains tentative until the user approves it and the generated `.agent/` records are applied.
