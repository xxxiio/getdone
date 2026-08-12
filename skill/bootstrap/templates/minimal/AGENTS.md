---
template: project-agents
template_version: 1.3.0
project_owned: true
---

# Project Agent Instructions

Before development:

1. Read `.agent/skills-reference.md` and verify `.agent/skills.lock.json`.
2. Read `skill/START-HERE.md` from the shared checkout.
3. Classify the implementation through `skill/workflow-router.md`, including whether the
   request uses task workflow or project workflow.
4. Read project context required by the work.
5. In task workflow, do not read or update the current next step unless the request
   specifically depends on continuation state.
6. In project workflow, read and maintain the current next step.
7. Load only the selected recurring guidance and historically relevant journal entries.
8. Keep project-owned history and continuation state inside this project's `.agent/`
   directory.

Treat the shared skill pack as read-only unless the task explicitly changes it.

Project-owned `.agent/` records follow the controlled project-record contract in the
shared skill pack. Run `getdone-validate-project` before claiming completion.
