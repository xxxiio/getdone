# Organisation Catalogue Overlay Example

This directory demonstrates an organisation-owned extension to the shared catalogue.

The overlay:

- uses the `org.example.*` namespace;
- keeps its Markdown guidance beside its registry file;
- may relate entries to canonical core identifiers;
- is loaded explicitly and never mutates the core registry.

Validate and search it with:

```bash
getdone-validate-overlay \
  --repository-root /path/to/getdone \
  --overlay registry-overlay.json

getdone-search \
  --repository-root /path/to/getdone \
  --overlay registry-overlay.json \
  --query "audit event envelope"
```
