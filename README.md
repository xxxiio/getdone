# GetDone
See [Repository usage](docs/usage.md) for adoption and maintainer instructions.


An agent-neutral, Markdown-first development workflow pack with optional Python tooling.

## Repository boundary

The filesystem has one authoritative product boundary:

```text
skill/        read-only content consumed by agents and projects
```

Everything outside `skill/` develops, validates, packages, or explains that product:

```text
getdone/      command-line implementation
tests/        contract and safety tests
development/  maintainer-only tools, entry points, benchmarks, and rollout evidence
docs/         maintainer and user documentation
examples/     repository-development examples
.github/      CI configuration
```

A consuming project's mutable plans, journals, reports, decisions, and TODOs belong in
that project's `.agent/` directory. They never belong in this repository.

## Operating model

GetDone has two agent-facing surfaces with different responsibilities:

- **Project-owned `.agent/` records** hold the current project context, plans, tasks,
  evidence, decisions, risks, and next deterministic step. Agents read and update these
  files during normal work.
- **The shared `skill/` pack** supplies read-only workflows, standards, acceptance gates,
  policies, and record contracts. Agents load only the documents selected for the current
  task.
- **The `getdone` CLI** bootstraps records, selects relevant guidance, validates contracts,
  runs diagnostics, and generates planning prompts. It is a deterministic guardrail, not
  the agent's working memory.

A shell-capable coding agent may run the CLI directly. ChatGPT or another agent without
repository access can work from uploaded `.agent/` records and selected skill documents;
the user then applies the proposed files and runs local validation. The repository remains
the source of truth in both cases.

## Normal agent context

Agents do not read the whole pack. A normal single-language feature, bug-fix, or refactoring task loads
six canonical documents:

1. General deterministic workflow.
2. Task-specific workflow.
3. Core engineering standard.
4. The language standard for each materially affected implementation surface.
5. Core acceptance gate.
6. Applicable change-type gate.

Investigations normally load five. Policies and references are conditional and are read
only when their trigger applies. The selector supports Python, Rust, C++, Dart/Flutter,
q/kdb+, and TypeScript. Single-language tasks normally select six files. Polyglot tasks add one language standard per materially affected language; standards are not loaded merely because a language exists elsewhere in the repository.

## Document contracts

Canonical content is intentionally separated by purpose:

- **Procedures** define triggers, inputs, ordered steps, decisions, evidence, stop
  conditions, and completion criteria.
- **Standards** define rules, observable review triggers, required responses, exceptions,
  and evidence.
- **Acceptance gates** define pass, waiver, and failure conditions.
- **Policies** define when a cross-cutting constraint applies and the exact action and
  evidence it requires.
- **References** explain optional patterns, components, decisions, and worked examples;
  they are not mandatory context.

Repository validation rejects incomplete operational contracts. See
[`docs/content-architecture.md`](docs/content-architecture.md).

## Controlled project records

Project-owned `.agent/` records are governed by one semantic contract and one
machine-readable registry:

- `skill/contracts/project-records.md`
- `skill/contracts/project-records.json`

Draft records may retain guided comments. Ready, active, current, completed, recorded,
approved, passed, or final records require controlled statuses, exact section order,
stable IDs, binary criteria, evidence, and valid roadmap references. The contract is
loaded only when records are created or materially updated, not during ordinary coding.

## Install and start

Install the GetDone CLI from the `get-done` PyPI distribution:

```bash
python -m pip install get-done
getdone --version
```

GetDone tooling and the shared skill pack are deliberately separate. Pin a full checkout or
extract the product-only skill pack, then run:

```bash
getdone doctor --project-root . --skills-root /path/to/getdone-skill-pack
getdone init --project-root . --skills-root /path/to/getdone-skill-pack --profile standard
getdone context --skills-root /path/to/getdone-skill-pack --task-class feature --language python --language rust
getdone validate --project-root . --skills-root /path/to/getdone-skill-pack
```

Follow the [golden-path tutorial](docs/golden-path.md) for one complete iteration.

## What GetDone does not do

GetDone does not write application code by itself, replace project tests or CI, replace an
issue tracker, require one coding-agent vendor, approve waivers automatically, or guarantee
correctness merely because structural validation passes. It supplies bounded guidance,
project records, and evidence contracts; the consuming project remains authoritative for its
behaviour and release decisions.

## Distribution

GetDone releases three separate artefacts:

- Full source archive: product plus development infrastructure.
- Skill-pack archive: only `VERSION` and `skill/`.
- Python wheel: tooling only; point it at a full checkout or extracted skill pack.

See [`docs/distribution.md`](docs/distribution.md) and [`docs/package-naming.md`](docs/package-naming.md).

Run `python development/scripts/check_release.py --repository-root .` for the automated local release preflight.

PyPI publication is performed by the tag-only GitHub Actions workflow documented in
[`docs/releasing.md`](docs/releasing.md). The workflow accepts credentials only through the
`PYPI_API_TOKEN` secret in the protected `pypi` GitHub Environment and rejects tags that do
not point to the current `main` HEAD.

## Validate

```bash
python development/scripts/validate_repository.py --repository-root .
python development/scripts/validate_frontmatter.py --repository-root .
python -m development.tools.validate_skill_content --repository-root .
getdone-validate-records --project-root /path/to/project --skills-root .
python development/scripts/generate_indexes.py --repository-root .
python -m unittest discover -s tests
```

## Release status

`v1.0.0` is the first stable release, with the Typer umbrella CLI, diagnostics, packaging metadata, licensing, and one golden-path example.

## Release setup for maintainers

Repository-level release setup can be automated from a source checkout after GitHub CLI authentication:

```bash
python development/scripts/configure_github_release.py --repository OWNER/getdone
```

Add `--set-pypi-token` and provide the token on standard input to configure the protected `pypi` environment secret. See `docs/releasing.md`. This script is not included in the user wheel.
