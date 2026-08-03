# Agent Adapters

Adapters are thin entry points. They point agents to project instructions, the composition
lock, `skill/START-HERE.md`, and selected context without duplicating workflows,
standards, gates, or policies.

`manifest.json` defines supported delivery modes and project destinations. Installable
project-file templates are under `templates/`. Existing project files are preserved unless
overwrite is explicit.
