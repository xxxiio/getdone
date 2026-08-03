# Repository Architecture

## Product layer

`skill/` is the only agent-consumable product root. It contains operational workflows,
consolidated standards and gates, conditional policies and references, bootstrap sources,
adapters, registries, schemas, and public contracts. Core registry paths are validated to
remain inside this boundary.

## Development layer

The remaining top-level directories support the product but are not canonical agent
instructions:

- `getdone/`: Python commands and validation.
- `tests/`: contract, migration, safety, and packaging tests.
- `development/tools/`: implementation of maintainer checks, generators, packaging, and evidence validation.
- `development/scripts/`: stable source-checkout entry points for maintainer operations.
- `development/benchmarks/`: measured context-selection fixtures and results.
- `development/rollout/`: executable consuming-project adoption cases.
- `docs/`: human onboarding, architecture, compatibility, and release documentation.
- `examples/`: development examples that are not registry-backed product references.
- `.github/`: CI jobs.

## Project-local layer

A consuming project's `.agent/` directory stores mutable task context, validation
evidence, journals, milestones, reports, TODOs, risks, blockers, decisions, and waivers.
`skill/bootstrap/` is rendered into that project; generated files become project-owned.

## Context layer

`getdone/context_selection.py` returns paths and a digest, not a generated prompt. The
normal recurring set contains at most six product documents. Conditional policies and
references are loaded only after their triggers are encountered.

## Migration and safety layer

Template inspection is dry-run by default. Missing additions and verified-unmodified
replacements require separate authorisation. Modified, untracked, mismatched, invalid, or
ahead project files never enter an automated write path.

## Distribution layer

The full source archive supports maintainers. The product-only skill pack supports
consuming projects. The wheel contains tooling only and requires either a source checkout
or extracted skill pack supplied through `--skills-root` or `--repository-root`.
