# Codex Adapter

1. Read the consuming project's `AGENTS.md` and local instructions.
2. Verify `.agent/skills.lock.json` against the shared checkout.
3. Read `skill/START-HERE.md`, then classify through `skill/workflow-router.md`.
4. Load only the selected recurring context; do not preload the full `skill/` tree.
5. Keep mutable plans, reports, and TODOs in the consuming project's `.agent/` directory.
6. Treat the shared checkout as read-only unless the task explicitly changes the skill pack.
7. Consult `skill/registry/reuse-catalogue.json` only when a reuse trigger applies.

Codex uses the bootstrap-managed project `AGENTS.md`; no second adapter file is required.
