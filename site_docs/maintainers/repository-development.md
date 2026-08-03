---
title: "Repository development"
description: "How maintainers change workflows, standards, registries, templates, and documentation."
tags: ["maintainers", "development"]
---

# Repository development

## Source hierarchy

- Machine-readable registries and contracts are authoritative for generated indexes and catalogue pages.
- Workflow and standard Markdown files are authoritative for procedural content.
- `site_docs/catalogue/` is generated and must not be edited directly.

## Documentation commands

```bash
python development/scripts/generate_docs.py --write
python development/scripts/generate_docs.py
zensical serve
zensical build --strict
```

The first command regenerates catalogue pages. The second checks for drift. The Zensical strict build catches rendering and internal-reference problems.

## Change discipline

When adding or changing a workflow, reusable entry, language, adapter, schema, template, or CLI command:

1. Update its authoritative registry or source.
2. Regenerate indexes and documentation.
3. Add or update contract tests.
4. Run repository validation and the strict documentation build.
5. Update migration and release notes when the public contract changes.
