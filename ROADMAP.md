# Roadmap

## Milestone 1: Core operating system — complete in 0.1.0

- Shared versus project-local state boundary
- Deterministic development workflow
- Feature, bug-fix, refactoring, investigation, documentation, release, and incident paths
- Minimal and standard bootstrap profiles
- Core reporting and tracking templates
- Initial best practices and language guidance
- Acceptance gates and repository validation

## Milestone 2: Workflow depth — complete in 0.2.0

- Architecture design and migration workflows
- Database and schema-change workflow
- Performance optimisation workflow
- UI and mobile feature workflow
- Multi-agent task decomposition and handoff guidance
- Detailed language-specific best practices and acceptance gates

## Milestone 3: Template lifecycle — complete in 0.3.0

- Version-aware project template update checks
- Generated template digests and local-modification detection
- Deterministic parent-first profile inheritance with child overlays
- Profile-cycle, unknown-parent, source-path, and schema validation
- Read-only migration plans with unified diffs
- Dry-run migration application by default
- Separately authorised safe additions and verified-unmodified replacements
- Organisation profiles layered over standard templates
- Selected profile, profile version, and lineage recorded project-locally

## Milestone 4: Maintainability and complexity guardrails — complete in 0.3.0

- Function, method, type, file, module, and dependency complexity review triggers
- Soft thresholds that require engineering review rather than automatic rejection
- Cohesion-first module-boundary guidance
- Pattern discipline that avoids abstraction-driven accidental complexity
- Core maintainability acceptance gate
- Language-specific complexity interpretations for Python, q/kdb+, C++, Rust, and Dart/Flutter

## Milestone 5: Section-aware merge guidance — complete in 0.4.0

- Read-only ATX Markdown section analysis for modified managed templates
- Added, removed, heading-changed, content-changed, and reordered evidence
- Repeated-heading matching by content similarity and stable order
- Conservative probable-rename detection with confidence values
- JSON Schema, JSON output, and opt-in human-readable CLI reporting
- No automated write path for modified project-owned content

## Milestone 6: Distribution and adapters — implementation complete in 0.5.0

- Installation guidance for adjacent/global checkouts, submodules, vendored snapshots, and tooling-wheel-plus-checkout use
- Schema-backed, tested thin adapters for major coding agents
- Non-destructive adapter installation and consuming-project validation commands
- Minimal executable consuming-project example with end-to-end adoption tests
- Release metadata, annotated-tag, signature-verification, checksum, and packaging policy
- External publication remains blocked on an authorised maintainer signing key and configured remote

## Milestone 7: Reuse intelligence — complete in 0.6.0

- Rich shared-component contracts for common infrastructure boundaries
- Pattern decision records and worked examples
- Schema-backed workflow and reuse registries with stable identifiers
- Deterministic human and JSON catalogue search
- Cross-adapter registry references for ChatGPT, Codex, Claude Code, Cursor, and GitHub Copilot
- Validation of paths, relationships, metadata parity, and duplicate identifiers
- Advisory-only adoption that preserves engineering judgement and complexity discipline

## Milestone 8: Skill authoring and registry lifecycle — complete in 0.7.0

- Workflow and acceptance gate for proposing, reviewing, promoting, deprecating, replacing, and retiring reusable guidance
- Registry schema v2 with permanent IDs, aliases, introduction versions, deprecation versions, and active replacements
- Exact canonical ID and alias resolution with lifecycle metadata
- Generated human-readable indexes with drift validation
- Semantic compatibility policy for registry and search-result contract evolution
- Schema-backed organisation overlays with namespace isolation and explicit search loading
- Executable organisation-overlay example and validation command

## Milestone 9: Pinned composition and reproducibility — complete in 0.8.0

- Compact project-local lock for core guidance, profile templates, adapter contract, and organisation overlays
- Content digests that detect same-version drift without embedding canonical guidance in the project
- Strict project validation across agents and environments
- Overlay-version provenance in search and project validation output
- Read-only update planning with semantic compatibility classification
- Explicit lock writes that preserve locked overlays unless replacements are named
- Reproducible consuming-project adoption with pinned overlay evidence

## Milestone 10: Measured context selection — complete in 0.9.0

- Nine representative feature, bug-fix, refactoring, and investigation fixtures across all supported language families
- Static routing accuracy, required-document recall, missed-gate, and approximate-token measurements
- Compact path-and-digest selection manifest with no copied guidance or generated prompt bundle
- 100% route accuracy and required-document recall with zero missed acceptance gates
- 74.84% average and 74.52% minimum recurring-context reduction against the full core-guidance baseline
- Published benchmark drift validation in repository health checks

## Milestone 11: v1.0 rollout readiness — complete locally in 1.0.0-rc.4

- RC.1 established the executable dogfood matrix, frozen contracts, quickstart, and CI matrix.
- RC.2 corrected the product architecture from rollout feedback without adding capabilities.
- RC.3 controls project-owned records with fixed statuses, IDs, section order, evidence,
  and roadmap-to-next-step references.
- RC.4 adds complete language standards, impact declarations, evidence manifests,
  invariant registers, workflow output contracts, and usage guidance.
- `skill/` is now the only agent-consumable root; source tooling and evidence remain outside it.
- Always-loaded guidance is consolidated to five or six operational documents per normal task.
- Workflows, standards, gates, and policies have triggers, actions, evidence, and explicit completion or exception rules.
- A separate skill-pack archive contains only `VERSION` and `skill/`.
- Representative context remains about 3,829 tokens, 21.16% below RC.1 with 100% route and required-document recall.
- Three rollout cases still pass across Python, C++, Codex, Claude, and Cursor delivery paths.
- Public remote execution, signing, and independent vendor-model runs remain external rollout steps.
- Fix rollout blockers only, then publish `v1.0.0`.

## Pre-v1 stop rule

No new workflow category, language, pattern entry, registry concept, adapter, or automation is added before v1.0 unless dogfooding demonstrates that its absence is a rollout blocker. See `docs/rollout-plan.md`.
