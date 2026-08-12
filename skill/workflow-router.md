# Workflow Router

Select one primary implementation workflow before coding. Separately select the project
state workflow mode; the mode changes record reads/writes, not bootstrap structure or the
primary implementation workflow.

## Project state workflow mode

| Request shape | Mode | Record behaviour |
|---|---|---|
| One bounded request that can finish independently | task | Read only relevant stable/history state; write durable journal history; do not maintain continuation state |
| Ongoing goal spanning multiple tasks or sessions | project | Read/write applicable current, planning, evidence, status, and continuation state; also write durable journal history |

Task workflow may retrieve prior journal entries when the request or a durable decision
makes them relevant, but it does not load project history wholesale. Project workflow uses
`.agent/current/next-step.md` as the continuation authority.

## Primary implementation workflow

Select one primary workflow before implementation. Add a specialist workflow only when
its trigger is present.

| Task signal | Primary workflow |
|---|---|
| Whole-project discussion, MVP, or roadmap definition | `workflows/general/project-planning.md` |
| Approved milestone needing multi-iteration decomposition | `workflows/general/execution-planning.md` |
| New observable behaviour | `workflows/feature/tdd-feature-development.md` |
| Incorrect existing behaviour | `workflows/bug-fix/regression-first-bug-fix.md` |
| Structural change with preserved behaviour | `workflows/refactoring/characterisation-first-refactoring.md` |
| Bounded unknown or feasibility question | `workflows/general/technical-investigation.md` |
| Documentation only | `workflows/general/documentation-change.md` |
| Release or dependency maintenance | `workflows/general/release-maintenance.md` |
| Production impact requiring containment | `workflows/bug-fix/incident-response.md` |
| Architecture choice | `workflows/architecture/architecture-design.md` |
| Staged architecture replacement | `workflows/architecture/migration.md` |
| Database or persisted-schema change | `workflows/database/schema-change.md` |
| Measured performance bottleneck | `workflows/performance/measurement-first-optimization.md` |
| UI/mobile vertical slice | `workflows/ui-mobile/vertical-slice.md` |
| Parallel agent work | `workflows/collaboration/multi-agent-decomposition.md` |
| Session or ownership transfer | `workflows/collaboration/task-handoff.md` |
| Shared skill or registry change | `workflows/governance/skill-authoring-lifecycle.md` |

When a request mixes categories, select the workflow that defines the acceptance risk.
Example: a performance bug uses regression-first bug fixing plus the measurement-first
workflow. Record the combination in the task plan when project workflow is active.
