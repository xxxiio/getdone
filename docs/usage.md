# Repository Usage Guide

The canonical product-facing instructions are in [`skill/USAGE.md`](../skill/USAGE.md).

## Operating model

GetDone is both a skill pack and a tooling layer. Agents normally read and update the
project-owned `.agent/` records and load only the selected shared skill documents. The
`getdone` CLI bootstraps, selects, validates, diagnoses, and generates prompts; it does not
replace those files as the operational source of truth.

Coding agents with shell access should use the Markdown records and the CLI together.
Conversational agents without repository access should return proposed complete files for
the user to apply and validate locally.

Repository maintainers should additionally:

1. Work from a complete Git checkout.
2. Keep canonical product content under `skill/`.
3. Keep tooling, tests, benchmarks, rollout fixtures, and maintainer documentation outside `skill/`.
4. Add tests before changing contracts or validators.
5. Regenerate context and rollout evidence after any selected-document content changes.
6. Build and test the wheel and product-only skill pack independently before release.
7. Do not describe a release as public-ready until the release checklist, remote CI, installation smoke tests, migration tests, and external/internal rollout evidence are complete.

## Planning a project

Use `project-planning` when outcomes, MVP scope, or milestone order are still being discussed. Use `execution-planning` only after a milestone is approved and needs multiple reviewable slices. For ChatGPT, print a canonical prompt with `getdone planning-prompt --mode project` or `--mode execution`. Discussion remains tentative until the user approves it and the generated `.agent/` records are applied.
## Adopting an existing repository

Use [`docs/adopting-existing-project.md`](adopting-existing-project.md) for a current-state-forward migration. It covers minimal, standard, and gradual adoption; selective roadmap and ADR migration; ChatGPT-assisted planning; validation; and the explicit material that should remain in Git or existing trackers.
