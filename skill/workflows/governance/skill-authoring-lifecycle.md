---
id: workflow.governance.skill-authoring-lifecycle
version: 1.1.0
status: stable
parent: workflow.general.deterministic-development
required_outputs:
- skill proposal or change review
- registry and compatibility evidence
- migration or deprecation record
---

# Skill Authoring and Registry Lifecycle

## Use this when

- Use for adding or changing reusable workflow, standard, gate, policy, reference, or registry metadata.

## Do not use this when

- Do not use for project-specific guidance belongs in the consuming project or organisation overlay.

## Required inputs

- Concrete repeated failure or reasoning cost.
- Target audience, trigger, overlap, token impact, and compatibility requirement.

## Procedure

1. Propose the behavioural gap and why existing content cannot cover it.
2. Choose procedure, standard, acceptance gate, policy, or optional reference.
3. Write operational triggers, actions, evidence, exceptions, and examples.
4. Add validation and registry lifecycle metadata.
5. Measure mandatory context impact and consolidate overlap.
6. Regenerate indexes and document migration or deprecation.

## Decision points

- Prefer editing/consolidating existing guidance over adding a file.
- Keep IDs permanent; use aliases and active same-kind replacements.

## Required evidence

- Proposal, tests, schema/index validation, context impact, compatibility, and review record.

## Stop conditions

- No demonstrated repeated value or the content remains vague.

## Completion criteria

- The change reduces repeated reasoning without unnecessary mandatory context.
