# Agent Development Skill Pack

This directory is the complete read-only product consumed by agents and projects.
Everything outside `skill/` develops, tests, packages, or explains the product.

## Load order

Start with `START-HERE.md`. For recurring work, use the path set returned by
`getdone-select-context` instead of preloading this directory.

A normal task loads five or six documents. Policies and references are conditional.
Schemas, templates, registries, and unrelated language material are not normal prompt
context.

## Content types

- `workflows/`: executable procedures.
- `standards/`: consolidated core and language rules.
- `acceptance/`: evidence-based completion gates.
- `policies/`: triggered cross-cutting constraints.
- `references/`: optional components, patterns, decisions, and examples.
- `bootstrap/`: sources rendered into consuming projects.
- `adapters/`: thin agent-specific entry points.
- `registry/`, `schemas/`, `contracts/`: machine discovery and compatibility contracts.
