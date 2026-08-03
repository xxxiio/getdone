# Reuse Intelligence

## Purpose

The reuse catalogue helps agents and developers discover an existing workflow, shared component, design pattern, decision record, or worked example before creating a new abstraction. Search results are advisory. They do not require reuse or pattern adoption.

## Canonical registries

- `skill/registry/workflows.json` indexes canonical workflow Markdown.
- `skill/registry/reuse-catalogue.json` indexes shared components, design patterns, decision records, and worked examples.
- JSON Schemas under `skill/schemas/` define the machine-readable contracts.

Repository validation confirms that canonical IDs and aliases are unique, paths exist, related and replacement identifiers resolve, lifecycle metadata is coherent, and workflow registry metadata matches canonical workflow front matter and headings. Human-readable indexes are generated from these JSON sources.

## Search

Search by a concrete task or design problem:

```bash
getdone-search \
  --repository-root /path/to/getdone \
  --query "transient failure backoff"
```

Apply optional filters:

```bash
getdone-search \
  --repository-root /path/to/getdone \
  --query "object construction" \
  --kind design-pattern \
  --language python \
  --tag object-creation
```

Use JSON when another agent or tool will consume the result:

```bash
getdone-search \
  --repository-root /path/to/getdone \
  --query "state transitions" \
  --json
```

The result includes why an item may fit, when it should be avoided, related entries, lifecycle metadata, source provenance, and the canonical Markdown path. Use `--id` for exact canonical or alias resolution, and `--overlay` to load an organisation-owned registry explicitly.

## Decision rule

Search before designing common infrastructure or introducing a pattern, then make an explicit decision:

1. Reuse an existing component or pattern because its semantics match.
2. Adapt an existing boundary because most semantics match but an external interface differs.
3. Keep the implementation local because ownership, lifecycle, or domain meaning differs.
4. Propose a new catalogue entry only after real reuse evidence exists.

A catalogue match is not acceptance evidence. The consuming task must still justify the boundary, test its contract, and satisfy complexity and maintainability gates.

## Adding an entry

A new entry must:

- Use a stable unique ID.
- Point to a focused Markdown document.
- State concrete use and avoidance conditions.
- Declare applicable languages and searchable tags.
- Link only to existing related identifiers.
- Pass repository and schema validation.

Shared components should also satisfy `skill/references/shared-components/component-checklist.md`. All additions and lifecycle transitions follow `docs/skill-authoring.md` and `skill/policies/registry-compatibility.md`.
