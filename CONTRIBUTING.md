# Contributing

Changes should improve repeatability, clarity, or verifiability across multiple projects or agents. Skill and registry changes must follow `skill/workflows/governance/skill-authoring-lifecycle.md`.

## Contribution rules

Until v1.0, accept only rollout-blocking fixes. New workflow families, languages, adapters, registry
concepts, and optional automation belong in the post-v1 backlog.


- Keep canonical workflow text agent-neutral.
- Prefer normative words deliberately: **must** for requirements, **should** for strong defaults, and **may** for optional behaviour.
- Avoid duplicating general guidance in language-specific files.
- Do not add mutable project state from consuming repositories.
- Add examples only when they clarify a reusable rule.
- Add validation for new required structures.
- Register reusable components, patterns, decisions, examples, and workflows with permanent canonical IDs and concrete use/avoid conditions.
- Preserve renamed identifiers as aliases; never reuse a retired canonical ID.
- Deprecate through an active same-kind replacement and explicit migration guidance.
- Keep organisation extensions in namespace-owned overlays unless the guidance is broadly reusable upstream.
- Regenerate human-readable indexes after every approved registry change.
- Record breaking workflow or template changes in `CHANGELOG.md`.
- Increment a template version whenever generated structure or required semantics change.
- Add migration guidance for material or breaking template changes.
- Keep profile inheritance acyclic and use child templates only for intentional additions or overrides.
- Treat complexity thresholds as review triggers and justify exceptions without gaming metrics.

## GitHub contribution templates

Use the structured GitHub templates under `.github/ISSUE_TEMPLATE/` for bug reports,
features, documentation improvements, and reusable workflow or skill proposals. Pull
requests must complete `.github/pull_request_template.md`, including change-impact,
compatibility, context-budget, migration, and validation evidence.

Security vulnerabilities must not be filed as public issues; follow `SECURITY.md`.

## Validation

```bash
python getdone/validate_repository.py
python getdone/validate_frontmatter.py
python getdone/generate_registry_indexes.py
python getdone/rollout_validation.py --repository-root . --check
python -m pytest
python -m compileall tooling tests
git diff --check
```
