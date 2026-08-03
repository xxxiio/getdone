---
id: workflow.general.documentation-change
version: 1.1.0
status: stable
parent: workflow.general.deterministic-development
required_outputs:
- verified documentation update
- documentation validation evidence
- evidence manifest
---

# Documentation-Only Change

## Use this when

- Use for the requested output changes documentation without changing runtime behaviour.

## Do not use this when

- Do not use for documentation is required because runtime behaviour also changes; use that primary workflow.

## Required inputs

- Verified current behaviour, target audience, and affected docs.

## Procedure

1. Reproduce or inspect the behaviour being documented.
2. Identify claims, examples, commands, and links that need change.
3. Write the smallest coherent update.
4. Run examples, link checks, or generated-doc checks where available.
5. Confirm no code behaviour was changed.

## Decision points

- Do not document unimplemented or assumed behaviour.
- Prefer one canonical explanation over duplicated copies.

## Required evidence

- Verified examples, links/check results, and changed audience-facing claims.

## Stop conditions

- Required behaviour cannot be verified.

## Completion criteria

- Documentation matches current behaviour and runnable examples succeed.
