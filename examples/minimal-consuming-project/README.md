# Minimal Consuming Project

This intentionally small Python project demonstrates adoption without copying shared workflows into the application repository.

From a checkout of `getdone`:

```bash
getdone-init \
  --project-root /path/to/this-project \
  --skills-root /path/to/getdone \
  --profile standard

getdone-install-adapter \
  --project-root /path/to/this-project \
  --skills-root /path/to/getdone \
  --adapter claude

getdone-validate-project \
  --project-root /path/to/this-project \
  --skills-root /path/to/getdone
```

The generated `.agent/` directory belongs to the consuming project. The shared repository remains read-only.

## Pinned guidance

Bootstrap creates `.agent/skills.lock.json`. Verify it before agent work with `getdone-lock --project-root . --skills-root /path/to/getdone`. When organisation guidance is used, pass the overlay to bootstrap so its version and referenced Markdown are pinned.
