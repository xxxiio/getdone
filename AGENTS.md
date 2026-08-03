# Repository Agent Instructions

This repository develops the Agent Development Skill Pack.

## Boundary

- `skill/` is the canonical read-only product.
- `getdone/`, `tests/`, `development/`, `docs/`, and `.github/` are repository-development
  infrastructure. `development/` holds maintainer-only tools, entry points, benchmarks, and rollout
  evidence.
- Mutable state for another project must never be written here; it belongs in that
  project's `.agent/` directory.

## Repository work

1. Read `skill/START-HERE.md` and select the applicable workflow.
2. Use `skill/workflows/governance/skill-authoring-lifecycle.md` for product-content or
   registry changes.
3. Keep recurring task context consolidated; a new mandatory document requires measured
   evidence that it can be omitted from other tasks.
4. Write procedures, standards, gates, and policies as operational contracts, not broad
   advice.
5. Add or update tests for workflow, registry, bootstrap, schema, or path changes.
6. Regenerate machine-derived indexes and benchmark evidence; do not edit generated
   indexes manually.
7. Do not add new capability categories before v1.0 unless rollout evidence identifies a
   blocker.

Explicit current human instructions take precedence, subject to safety and repository
permissions.
