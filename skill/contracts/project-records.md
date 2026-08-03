# Controlled Project Record Contract

## Purpose

This contract governs project-owned Markdown records created by the bootstrap profiles. It
prevents agents from inventing headings, statuses, identifiers, completion meanings, or
update behaviour on each run.

The machine-readable authority is `project-records.json`. Bootstrap templates provide
compact field prompts. This document defines the semantic rules that are not practical to
express through Markdown structure alone.

Load this contract only when creating, materially updating, migrating, or reviewing a
controlled record. Ordinary implementation work reads the filled project record, not this
entire contract.

## Common rules

1. Keep the front-matter `record_contract` and `record_schema_version` unchanged unless a
   documented migration changes them.
2. Preserve the exact H2 heading set and order declared by the contract registry.
3. Use only controlled status values. Do not invent synonyms such as `almost-done`,
   `in-progress-ish`, or percentage-complete labels.
4. Draft or proposed records may retain the template's guided comments. Before changing a
   record to ready, active, current, completed, recorded, approved, passed, or final,
   replace every applicable placeholder with project facts.
5. Criteria must be binary, observable, and independently markable. Avoid `improve`,
   `support better`, `make scalable`, `add enough tests`, and similar unbounded wording.
6. Evidence names an exact command, test, artefact, issue, commit, report, or review. A
   statement such as `tested` is not evidence.
7. Use stable IDs. Never reuse an ID after cancellation, completion, supersession, or
   deletion.
8. Do not duplicate shared engineering rules inside project records. Record the
   project-specific application, decision, result, or evidence.
9. Current-state records contain present facts. Historical narrative belongs in journal
   entries; future ideas belong in TODO or deferred-work records.
10. User-approved priorities and scope override agent inference. Record the change and its
    effect rather than silently rewriting prior intent.

## Controlled status transitions

| Record | Normal transitions |
|---|---|
| Roadmap, project context, command reference, project status | `draft -> current` |
| Next step | `proposed -> ready -> completed`; `ready -> blocked`; any non-completed state may become `cancelled` |
| Task | `proposed -> ready -> active -> completed`; `active -> blocked -> active`; any unfinished state may become `cancelled` |
| Milestone | `proposed -> ready -> active -> completed`; `active -> blocked -> active`; unfinished milestones may become `deferred` or `cancelled` |
| Acceptance report | `draft -> incomplete | passed | failed | waived` |
| Journal entry | `draft -> recorded`; recorded entries are append-only corrections, not rewritten history |
| ADR | `proposed -> accepted | rejected`; accepted decisions may become `superseded` or `deprecated` |
| Waiver | `proposed -> approved -> expired | revoked` |
| Completion, progress, and handoff reports | `draft -> final` |

Reopening a completed milestone, task, or final report requires explicit human approval and
an explanation in a new journal entry. Do not silently move it backwards.

## Operational lifecycle

For one bounded iteration, update records in this order:

1. Define or revise the next deterministic step and its milestone exit criteria.
2. Make the current task ready or active with scope, acceptance criteria, and validation.
3. Record change impact before implementation; resolve or visibly retain unknown impacts.
4. Record actual acceptance and quality-gate evidence as work proceeds.
5. Finalise acceptance and evidence before marking the task completed.
6. Write the required completion or handoff report, then update the concise project status.
7. Create exactly one subsequent next step, or record why no next action is currently valid.

The roadmap remains an approved milestone plan; it is not rewritten as a task journal.
`project-status.md` is a concise summary and must not claim more than the current task,
evidence, acceptance, and register records prove. Use `getdone status` to inspect the
authoritative current-record summary and its consistency findings without modifying state.

## Roadmap

The roadmap is authoritative only for approved milestone outcomes and order. It is not a
feature wishlist, task plan, changelog, or journal.

- `current_milestone` must equal the single milestone whose status is `active`, or be null
  when none is active.
- At most one milestone may be active.
- A milestone ID uses `MILESTONE-NNNN` and is never reused.
- Milestone dependencies must reference IDs present in the same roadmap.
- Do not activate a milestone while a required dependency is incomplete.
- Each milestone outcome describes an observable state, not an implementation activity.
- Exit criteria use `EC-NNN`, are binary, and have a matching evidence row.
- Completed criteria remain visible with their evidence.
- Completed milestones are not rewritten to incorporate newly discovered work. Create a
  later milestone or explicit follow-up instead.
- Deferred work records both why it is deferred and the observable trigger for
  reconsideration.
- Do not use subjective completion percentages. Progress is represented by exit-criterion
  states and evidence.

Allowed milestone statuses are `proposed`, `ready`, `active`, `blocked`, `completed`,
`deferred`, and `cancelled`.

## Next deterministic step

The next-step record contains exactly one bounded objective that can be completed in one
reviewable iteration.

- The ID uses `NEXT-NNNN`.
- A ready, blocked, or completed step must reference a real roadmap milestone and at least
  one `EC-NNN` defined by that milestone.
- The objective describes one observable result. `Continue implementation`, `work on the
  backend`, and `improve quality` are invalid objectives.
- `Why this is next` explains why no higher-priority unfinished work should precede it.
- Preconditions are already-true conditions, not implementation actions.
- Inputs name exact paths, contracts, issues, APIs, or evidence.
- Ordered actions are executable and exclude optional later work.
- Outputs name concrete files, behaviours, decisions, or evidence.
- Acceptance criteria use `NS-NNN` and are binary.
- Validation contains exact executable commands.
- Stop conditions state when to halt, escalate, or re-plan.
- Out-of-scope items prevent unapproved expansion.
- A completed next step has all criteria checked and evidence recorded in the task
  acceptance or completion report.

## Task records

The current-task singleton and repeatable task records describe one unit of work.

- IDs use `TASK-NNNN` and reference an approved milestone when the status is not proposed.
- Current behaviour contains reproduced or observed facts.
- Desired behaviour contains externally observable post-change behaviour.
- Scope and out-of-scope lists must not overlap.
- Acceptance criteria use `AC-NNN`; completed tasks have every criterion checked.
- Validation commands are executable in the documented project environment.
- New unrelated findings become TODOs rather than being silently added to scope.

## Milestone plans and progress reports

A milestone plan expands one roadmap milestone without changing its approved outcome.

- The plan ID must match the roadmap milestone ID.
- Deliverables are concrete artefacts or behaviours.
- The implementation sequence is ordered into bounded iterations.
- Exit criteria use the same `EC-NNN` identities as the roadmap.
- Evidence maps directly to each criterion.
- A progress report lists criterion states as `met`, `unmet`, `blocked`, `waived`, or
  `not-applicable`; it does not estimate an overall percentage.

## Acceptance and completion reports

Acceptance is evidence, not narrative confidence.

- Gate status is one of `pass`, `fail`, `waived`, `not-applicable`, or `not-run`.
- `pass` names evidence proving the gate.
- `fail` states the failed condition and impact.
- `waived` references an approved `WAIVER-NNNN`.
- `not-applicable` explains why the gate trigger does not apply.
- `not-run` explains why it was skipped and the residual risk.
- A task completion report cannot claim successful completion while an applicable gate is
  failed or not-run unless an approved waiver explicitly permits it.

## Project context, commands, and status

- Project context contains stable facts and current priorities that change agent
  behaviour. It must not repeat generic language standards or workflow definitions.
- Command reference records exact executable commands. When the project declares one
  canonical full health gate, agents prefer it over reconstructing individual checks.
- Project status is concise and present-tense. It links milestone, task, ADR, risk,
  blocker, and next-step IDs instead of copying their full content.

## Journal, decisions, waivers, and registers

- Journal entries are dated, append-only historical evidence. Corrections are appended and
  identified; prior facts are not silently replaced.
- ADRs record one durable choice, alternatives, consequences, and validation. Accepted
  ADRs are changed only through supersession or deprecation.
- Waivers require an exact requirement, concrete risk, compensating control, owner,
  approval evidence, and an expiry date or observable removal condition. Open-ended
  waivers are invalid.
- Risk rows describe a possible event and trigger. Blocker rows describe a condition that
  is already preventing work. TODO rows describe actionable work. Dependency rows name a
  requirement of another work item. Do not use these registers interchangeably.

## Validation

Validate project records directly:

```bash
getdone-validate-records \
  --project-root /path/to/project \
  --skills-root /path/to/skill-pack
```

Normal project validation includes the same checks:

```bash
getdone-validate-project \
  --project-root /path/to/project \
  --skills-root /path/to/skill-pack
```

Validation checks structure and cross-record consistency. Human review remains responsible
for whether the stated facts and evidence are truthful.

## Structural execution records

### Change impact declaration

Use `.agent/current/change-impact.md` before implementation. Every impact dimension is `yes`, `no`, or `unknown`. A `yes` value must name the activated specialist gate. An `unknown` value must remain visible until verified or converted into a blocker. The declaration controls conditional outputs and the minimum test tier; it is not a narrative risk essay.

### Evidence manifest

Use `.agent/current/evidence.md` as the source of truth for completion claims. A passed acceptance criterion requires concrete evidence. A passed quality gate requires the command or artefact and its result. Skipped checks require reason and impact. Completion reports may summarise this record but must not claim more than it proves.

### Invariant register

Use `.agent/invariants.md` for a small set of critical truths whose violation would materially damage architecture, correctness, data integrity, security, or operations. Active invariants require an enforcement mechanism and a review trigger. Do not use the register for preferences, style rules, or ordinary acceptance criteria.

## Test tiers

- Tier 1: changed unit tests.
- Tier 2: affected module or package tests.
- Tier 3: relevant integration and contract tests.
- Tier 4: canonical full repository health gate.

Use the lowest tier that covers the declared impact. Public API, persistence, dependency, concurrency, security-boundary, deployment, and similarly broad changes normally require Tier 3 or Tier 4 evidence.

## Authority hierarchy

Current user instructions take precedence. Then use accepted policies and decisions, active milestone scope, current task, current next step, current project status, roadmap ordering, and finally historical records. Commands come from the command reference. Acceptance claims come from the evidence and acceptance records. Historical journals do not override current approved state.
