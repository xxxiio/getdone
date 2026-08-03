---
id: workflow.general.deterministic-development
version: 1.3.0
status: stable
applies_to:
  - feature
  - bug-fix
  - refactoring
  - investigation
  - maintenance
required_outputs:
  - current task
  - impact declaration
  - evidence manifest
  - completion report
  - next step
conditional_outputs:
  public_api:
    - compatibility and API docs
  persisted_data:
    - migration and rollback
  architecture:
    - decision record
  deployment:
    - deployment and rollback
---

# Deterministic Development Workflow

## Use this when

- Any bounded coding, configuration, test, documentation, or repository-maintenance task.

## Do not use this when

- Unbounded product discovery; first create a bounded investigation or milestone.

## Required inputs

- Current human request and project instructions.
- Project context, commands, current task, and next step when present.
- Selected task workflow, core and affected-language standards, and applicable gates.

## Procedure

1. Verify the project lock and separate shared read-only content from project-owned state.
2. Inspect relevant code, architecture, tests, and commands; run the declared test-tier baseline or canonical health command. If neither exists, run the smallest reproducible relevant check and record that gap.
3. Write observable acceptance criteria, scope, exclusions, risks, and the smallest coherent slice; declare impacts first.
4. Follow the selected task workflow's evidence pattern: feature and bug-fix work starts with failing behavioural or regression evidence; refactoring starts with characterisation evidence; investigation starts with an experiment or source inspection; documentation-only work validates the documented behaviour or records why it cannot.
5. Run applicable project-defined format, lint, type, test, build, security, and performance checks.
6. Update documentation and evidence; record skipped checks, risks, decisions, and conditional outputs project-locally.
7. Evaluate the core and change-type gates; define one next deterministic step if work continues.

## Decision points

- If baseline checks already fail, record them separately before changing code.
- If a task crosses workflow categories, keep one primary workflow and add only the specialist procedure needed for the risk.
- If an acceptance criterion cannot use its primary automated proof, name the unavailable proof, alternative evidence, and resulting limitation before implementation.

## Required evidence

- Acceptance criteria and scope.
- Tests or reproductions before and after the change where applicable.
- Commands run, outcomes, skipped checks, and pre-existing failures.
- Documentation and project-state updates.
- Final gate statuses and next step.

## Stop conditions

- Destructive action lacks authority.
- Required credentials, permissions, or external decisions are unavailable.
- Continuing would conceal a blocking failure, security issue, or data-loss risk.
- Instructions conflict and precedence does not resolve them.

## Completion criteria

- The bounded objective is met.
- All applicable evidence is recorded and gates pass or have an explicit status.
- No unrelated work is silently included.
- Remaining work is project-local and the next step is singular and testable.
