# Organisation Catalogue Overlays

An overlay extends discovery without modifying or copying the core registry. It is owned, versioned, and distributed by the organisation that defines it.

## Identity

An overlay declares a short namespace. Reuse entries use `org.<namespace>.*`; workflow IDs use `workflow.org.<namespace>.*`. Core IDs and aliases cannot be shadowed.

## Layout

```text
organisation-overlay/
├── registry-overlay.json
└── skill/references/
    └── shared-components/
        └── example.md
```

Paths in the overlay are relative to `registry-overlay.json`. Guidance remains Markdown and registry metadata remains JSON.

## Validation

```bash
getdone-validate-overlay \
  --repository-root /path/to/getdone \
  --overlay /path/to/organisation-overlay/registry-overlay.json
```

Validation checks the overlay schema, namespace ownership, document paths and headings, workflow metadata, lifecycle rules, relationships, and collisions with core IDs and aliases.

## Search

```bash
getdone-search \
  --repository-root /path/to/getdone \
  --overlay /path/to/organisation-overlay/registry-overlay.json \
  --query "audit event envelope"
```

Multiple overlays may be supplied explicitly. Search output identifies each result source. Consumers should pin the core repository release and every overlay version used in deterministic automation.

## Contribution boundaries

- Put organisation policy and internal component contracts in the overlay.
- Contribute broadly reusable, non-confidential guidance upstream to the core repository.
- Do not use overlays to replace or weaken core safety and acceptance requirements.
- Do not copy live project plans, journals, secrets, or task state into an overlay.

See `skill/references/examples/organisation-catalogue-overlay/` for an executable example.
