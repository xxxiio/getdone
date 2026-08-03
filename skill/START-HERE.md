# Start Here

## Operating model

Use project-owned `.agent/` records as the current operational state and load only the
selected read-only skill documents for the task. Use the `getdone` CLI to bootstrap, select,
validate, and diagnose; do not treat the CLI or the complete skill repository as the
agent's working context.
See [How to Use This Skill Repository](USAGE.md) for installation, task execution, record authority, validation, and maintenance.


## Purpose

Use this pack to execute one bounded development task consistently. Mutable plans,
journals, TODOs, and reports belong in the consuming project's `.agent/` directory,
never in this shared pack.

## One-time project startup

1. Read the current human instruction and the project's `AGENTS.md`.
2. Locate the shared checkout through `.agent/skills-reference.md`.
3. Verify `.agent/skills.lock.json` with `getdone-lock`.
4. Read project context, command reference, current task, and next step when present.
5. Classify the task through `workflow-router.md`.

## Recurring task context

For feature, bug-fix, refactoring, or investigation work, load only the five or six canonical
documents returned by `getdone-select-context`:

1. General deterministic workflow.
2. Task-specific workflow.
3. Core engineering standard.
4. Language standards for every materially affected implementation surface.
5. Core acceptance gate.
6. Applicable change-type gate.

Load a policy or reference only when its stated trigger applies. Do not read every
standard, policy, pattern, or component guide by default.

## Controlled project records

When creating or materially updating a `.agent/` record, follow
`contracts/project-records.md` and run `getdone-validate-records`. Do not load that
contract for ordinary code work when the filled records are already valid.

## Project-state boundary

- `skill/` is shared and read-only during normal project work.
- `.agent/` in the consuming project is mutable and project-owned.
- Changes to this skill pack require the skill-authoring workflow and repository tests.

## Completion rule

Do not report completion until required evidence is recorded, applicable gates pass or
have an explicit status, remaining work is captured, and one next deterministic step is
identified when the project continues.
