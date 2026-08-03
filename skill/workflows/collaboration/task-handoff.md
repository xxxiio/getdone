---
id: workflow.collaboration.task-handoff
version: 1.1.0
status: stable
parent: workflow.general.deterministic-development
required_outputs:
- handoff report
- repository state evidence
- next deterministic step
---

# Task Handoff

## Use this when

- Use for work changes session, agent, or owner before the project is complete.

## Do not use this when

- Do not use for the task is complete and no continuation context is needed.

## Required inputs

- Current objective, repository state, evidence, blockers, and next step.

## Procedure

1. Summarise completed behaviour, not activity alone.
2. List exact changed paths and commands run.
3. Record failures, risks, decisions, and uncommitted state.
4. Define one executable next step with inputs and acceptance criteria.

## Decision points

- Distinguish verified facts from hypotheses.
- Do not hide partial or failing work behind a completion label.

## Required evidence

- Handoff report, repository status, validation results, and next step.

## Stop conditions

- Repository state cannot be described accurately.

## Completion criteria

- Another competent agent can continue without rediscovering material context.
