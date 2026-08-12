# Start Here

## Operating model

Bootstrap establishes the project's complete `.agent/` state once. Task and project are
workflow modes only: they determine which existing records the agent reads and writes for
the current request.

Load only the selected read-only skill documents for the work. Use the `getdone` CLI to
bootstrap, select, validate, and diagnose; do not treat the CLI, the complete skill
repository, or the complete `.agent/` tree as the agent's working context.

See [How to Use This Skill Repository](USAGE.md) for installation, workflow modes, record
authority, validation, and maintenance.

## Purpose

Use this pack to execute bounded development work consistently while preserving durable
project memory. Mutable plans, journals, TODOs, and reports belong in the consuming
project's `.agent/` directory, never in this shared pack.

## One-time project startup

1. Read the current human instruction and the project's `AGENTS.md`.
2. Locate the shared checkout through `.agent/skills-reference.md`.
3. Verify `.agent/skills.lock.json` with `getdone-lock`.
4. Classify the work through `workflow-router.md`, including task versus project workflow.
5. Read only the project records required by that workflow mode.

Task workflow normally reads stable project facts plus relevant guidance and historical
journal entries only when needed. Project workflow additionally reads current, planning,
status, evidence, and continuation records required by the active goal.

## Recurring task context

For feature, bug-fix, refactoring, or investigation work, load only the five or six canonical
documents returned by `getdone-select-context`:

1. General deterministic workflow.
2. Task-specific workflow.
3. Core engineering standard.
4. Language standards for every materially affected implementation surface.
5. Core acceptance gate.
6. Applicable change-type gate.

Load a policy, reference, project record, or prior journal entry only when its stated
trigger or historical relevance applies. Do not read every standard, policy, pattern,
component guide, project record, or journal entry by default.

## Controlled project records

When creating or materially updating a `.agent/` record, follow
`contracts/project-records.md` and run `getdone-validate-records`. Do not load that
contract for ordinary code work when the filled records are already valid.

## Project-state boundary

- `skill/` is shared and read-only during normal project work.
- `.agent/` in the consuming project is mutable and project-owned.
- Bootstrap structure is independent of task/project workflow selection.
- Changes to this skill pack require the skill-authoring workflow and repository tests.

## Completion rule

In task workflow, do not report completion until the bounded outcome is validated and a
durable journal entry records the work and findings; there is no next-step obligation.

In project workflow, also keep the applicable current/evidence/status records accurate and
identify exactly one next deterministic step, or record a justified no-change state.
