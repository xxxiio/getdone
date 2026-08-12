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

Bootstrap is normally run once. Use the standard profile for the normal full GetDone project state; task/project workflow selection happens later and does not change bootstrap:

```bash
getdone-init \
  --project-root /path/to/project \
  --skills-root /path/to/skill-pack \
  --profile standard
```

Bootstrap files under `.agent/` are project-owned. Edit those records in the project; do not edit shared `skill/` content to record project state.

## Choose a project-state workflow

Task and project differ only in which already-bootstrapped records the agent reads and
writes.

**Task workflow** is for one bounded request. Read applicable workflow/project guidance,
stable project facts, and only historically relevant journal entries. Write the
implementation, validation evidence, journal history, and durable decisions when needed.
Normally leave current-task, roadmap, plans, status, handoff, and next-step records
untouched.

**Project workflow** is for an ongoing goal spanning multiple tasks or sessions. Use the
same implementation guidance and journal history, plus the current, planning, evidence,
status, reporting, and continuation records required by the active goal. Maintain
`.agent/current/next-step.md` as the continuation authority.

## Start a task

1. Verify the composition lock.
2. Let the coding agent inspect the repository and identify likely affected implementation surfaces.
3. Select the project-state workflow mode and one primary implementation workflow.
4. Load only the selected workflow, applicable standards/project guidance, and project records required by the chosen mode.


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

## Finish work

In **task workflow**, run applicable repository validation, write a recorded journal entry
with completed work and durable findings, and do not create continuation state merely to
close the bounded request.

In **project workflow**, also update applicable current/evidence/status/report records and
define exactly one next deterministic step, or record a justified no-change outcome.

Validate project records:

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
