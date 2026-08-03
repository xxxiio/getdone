---
title: Planning with GetDone
description: Discuss, approve, and record whole-project and milestone execution plans with coding agents or ChatGPT.
tags:
- planning
- chatgpt
---

# Planning with GetDone

GetDone separates two planning problems:

- **Project planning** decides the outcome, users, MVP, boundaries, milestones, dependencies, risks, and what happens first.
- **Execution planning** decomposes one approved milestone into independently reviewable slices.

Both workflows support ordinary conversation. Draft discussion remains tentative until the user approves it. In commitment mode, an agent updates project files; ChatGPT can instead return separately labelled Markdown artefacts for each target path.

## ChatGPT project-planning prompt

```text
Use GetDone's project-planning workflow. Begin in discovery mode. Keep a decision ledger with agreed, tentative, unknown, and deferred items. Do not treat suggestions as approved. Once I approve the direction, generate the controlled project plan, project context, roadmap, first milestone, risks, dependencies, invariants where needed, and exactly one next deterministic step. Label every Markdown artefact with its target .agent path.
```

## ChatGPT execution-planning prompt

```text
Use GetDone's execution-planning workflow for the approved milestone. Decompose it into stable, dependency-aware, independently reviewable slices with binary acceptance criteria, must-not-change conditions, validation tiers, integration order, and stop conditions. After approval, generate the execution-plan record and exactly one next-step record, each labelled with its target .agent path.
```

## Authority

Discussion notes are not authoritative project state. Only approved and applied records are authoritative. When ChatGPT cannot edit the repository, the user must save or apply the generated artefacts before GetDone can validate them.
