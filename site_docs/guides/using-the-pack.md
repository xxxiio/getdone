---
title: "Using the skill pack"
description: "Practical guidance for consuming projects and coding agents."
tags: ["guide", "usage"]
---

# Using the skill pack

## What the agent uses

The agent's normal working context is the project's `.agent/` records plus a small,
task-selected subset of the shared skill pack. The CLI is the bootstrapper, selector,
validator, and diagnostic layer around those files.

- Shell-capable coding agents can read and update the files and run `getdone` directly.
- ChatGPT-style agents can work from uploaded records and selected guidance, return complete
  proposed file replacements, and leave local validation to the user.
- The committed repository files remain authoritative; chat uploads and discussion notes do
  not silently replace them.

## For project owners

- Pin a specific skill-pack version.
- Keep the extracted `skill/` directory read-only.
- Bootstrap project-owned files once, then edit only the project copies.
- Record canonical commands in `.agent/command-reference.md`.
- Migrate templates through the provided migration tooling instead of replacing files manually.

## For coding agents

- Start from `AGENTS.md`, project context, and the current next step.
- Use the context selector rather than browsing all guidance.
- Search the reuse catalogue before introducing a new abstraction.
- Treat change-impact dimensions marked `unknown` as unresolved, not as `no`.
- Never report a passed gate without evidence.
- Finish with one bounded next deterministic step.
- Use `getdone status` for a read-only summary before a handoff, review, or resumed session.

## For organisations

Organisation-specific policy and reusable components should be added through overlays. Do not fork and rewrite the core registry unless the shared public contract itself must change.

## Planning a project

Use `project-planning` when outcomes, MVP scope, or milestone order are still being discussed. Use `execution-planning` only after a milestone is approved and needs multiple reviewable slices. For ChatGPT, print a canonical prompt with `getdone planning-prompt --mode project` or `--mode execution`. Discussion remains tentative until the user approves it and the generated `.agent/` records are applied.
## Adopting an existing project

For an established repository, use the [existing-project adoption guide](adopting-existing-project.md). Migrate current authoritative state rather than recreating all project history, and begin evidence-backed operation on the next real task.
