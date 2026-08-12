# Changelog

All notable public changes to GetDone will be documented in this file.

Detailed pre-release development history remains available in Git history and
`docs/iterations/`; it is not a public migration contract.

## 1.1.0 - 2026-08-11

### Added

- Optional `.project-agent/` project extensions with an always-loaded `AGENTS.md` baseline and indexed, bounded project-specific guidance.
- Automatic affected-language inference from repeated `--changed-path` values while retaining repeatable `--language` for explicit polyglot selection.
- `getdone project-agent validate` and `getdone project-agent inspect` for project-extension health and selection diagnostics.
- `getdone doctor --project-agent auto|required|off`, with default warnings when a project-specific extension is absent and deep validation when one is present.
- Pytest as the canonical repository test runner, installed through the `test` extra.

### Changed

- `getdone guidance` discovers `.project-agent/` from `--project-root`, infers project-defined concerns from known or anticipated affected paths, and composes matching project guidance without teaching GetDone project-specific semantics.
- `--changed-path` is a guidance-routing signal, not a source-file or model-context selection mechanism.
- Bootstrap remains a one-time project-state setup; task and project are workflow modes that differ only in which existing records agents read and write.
- Journal entries are durable historical memory only and no longer duplicate next-step continuation state.
- `.agent/` remains the mutable GetDone/project execution-state location; `.project-agent/` is the durable project-specific agent-extension boundary.
- Repository CI, contributor validation, and embedded Python test invocations now run through pytest instead of `unittest discover`.

## 1.0.0 - 2026-08-03

### Added

- `getdone status`, a read-only Markdown or JSON summary of authoritative current records and record-consistency findings.
- Rendered documentation pages for every bootstrap/governance template and coding-agent adapter, linked from their catalogue inventories.
- Structured GitHub issue forms and a pull-request template for bugs, features, documentation, reusable skill proposals, compatibility, and validation evidence.
- GitHub Pages deployment for the Zensical documentation site from `main`.
- Conversational project planning and milestone execution planning for coding agents and ChatGPT.
- Controlled project-plan and execution-plan records with dependency validation.
- `getdone planning-prompt` for ready-to-copy ChatGPT planning sessions.
- Typer-based `getdone` CLI, project diagnostics, golden-path adoption material,
  generated documentation catalogues, controlled project records, deterministic
  context selection, evidence validation, and language-specific engineering standards.

### Removed

- Unreleased `agent-skills-*` command aliases and the `tooling` import shim. The first public release exposes only canonical `getdone` names.

### Changed

- Tightened recurring workflow evidence by task class, made language standards explicitly impact-scoped, consolidated overlapping core structural guidance, and made all change-type waiver evidence explicit.
- Context selection now supports polyglot tasks by accepting repeated `--language` options and loading one standard for each materially affected language.
- Documented the stable naming contract: GetDone product, `getdone-dev` PyPI distribution, and `getdone` CLI/import namespace.
- The public product identity is GetDone, distributed as `getdone-dev` and invoked
  through the `getdone` command.
- Pre-1.0 release-candidate migration notes and granular changelog entries were
  removed from the public release surface. Public compatibility history begins with
  the first stable release.

## 1.0.0-rc.9 - 2026-07-29

### Status

- Internal release candidate adding conversational project and execution planning.
- Not a stable public compatibility boundary.

## 1.0.0-rc.7 - 2026-07-26

### Status

- Internal release candidate used as the consolidated pre-1.0 baseline.
- Not a stable public compatibility boundary.
