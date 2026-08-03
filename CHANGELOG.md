# Changelog

All notable public changes to GetDone will be documented in this file.

Detailed pre-release development history remains available in Git history and
`docs/iterations/`; it is not a public migration contract.

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
- Documented the stable naming contract: GetDone product, `get-done` PyPI distribution, and `getdone` CLI/import namespace.
- The public product identity is GetDone, distributed as `get-done` and invoked
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
