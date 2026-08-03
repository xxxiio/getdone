---
id: workflow.general.project-planning
version: 1.0.0
status: stable
required_outputs:
- approved project plan or explicitly unresolved discovery record
- project context and roadmap updates in commitment mode
- first deterministic step
---

# Project Planning

## Use this when

- A user wants to shape a new project, define an MVP, compare major directions, or plan the whole project.
- Outcomes, scope, milestones, dependencies, or major risks are not yet agreed.

## Do not use this when

- The project direction is already approved and only one milestone needs implementation decomposition.
- The question is a bounded technical unknown; use technical investigation instead.

## Required inputs

- Initial problem, idea, or desired outcome.
- Known users, constraints, deadlines, and non-negotiable requirements.
- The decision owner and the level of commitment expected from this session.

## Modes

### Discovery mode

Discuss options, ask only decision-relevant questions, mark assumptions and unknowns, and avoid presenting tentative ideas as approved scope.

### Commitment mode

After the user approves the direction, write or update the controlled project plan, project context, roadmap, milestone, risks, dependencies, invariants, and first deterministic step.

## Procedure

1. Restate the problem and observable desired outcome for confirmation.
2. Identify primary users, use cases, success measures, constraints, assumptions, and unknowns.
3. Define scope and explicit non-goals before proposing implementation detail.
4. Compare only materially different directions against stated criteria.
5. Record the selected direction and durable decisions; create ADRs only when the decision threshold is met.
6. Define an MVP and order outcome-based milestones with dependencies and binary exit criteria.
7. Keep the active milestone detailed, the next milestone outcome-level, and later milestones coarse.
8. Convert high-impact unknowns into bounded investigations before dependent milestones.
9. Present the plan for approval before treating it as authoritative.
10. In commitment mode, emit the controlled records and exactly one first deterministic step.

## ChatGPT delivery

- During discussion, maintain a visible decision ledger: agreed, tentative, unknown, and deferred.
- When files cannot be edited directly, return each approved record in a separately labelled Markdown block with its target path.
- Never claim project records were updated unless the files were actually changed or the user explicitly accepted the generated artefacts.

## Decision points

- Stay in discovery mode until the user approves commitment.
- Prefer a bounded investigation over speculative sequencing when a high-impact unknown remains.

## Required evidence

- User-approved outcome, MVP boundary, and milestone order.
- Traceability from success measures to milestone exit criteria.
- Explicit assumptions, unknowns, dependencies, risks, and deferred work.

## Stop conditions

- The decision owner cannot approve the outcome or scope.
- A high-impact unknown prevents meaningful milestone ordering.
- The conversation remains brainstorming and the user has not requested commitment.

## Completion criteria

- The approved project direction is distinguishable from tentative discussion.
- The roadmap contains outcome-based milestones with dependencies and exit criteria.
- The MVP and non-goals are explicit.
- Exactly one first deterministic step is ready, or a bounded investigation is the first step.
