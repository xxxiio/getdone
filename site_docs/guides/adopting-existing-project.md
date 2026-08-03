---
title: "Adopting GetDone in an existing project"
description: "Migrate an existing repository to GetDone without recreating its entire history."
tags: ["guide", "migration", "adoption"]
---

# Adopting GetDone in an existing project

Use this guide for an existing package, library, service, application, monorepo, or other software repository.

A **software project** is the repository governed by GetDone. A **ChatGPT Project** is an optional ChatGPT workspace used to retain related chats, files, and instructions. The repository remains authoritative.

## Migrate current state, not all history

Establish a trustworthy baseline from today forward:

- stable project context;
- verified commands;
- the active milestone and task;
- current risks and dependencies;
- durable invariants;
- one next deterministic step.

Leave resolved history in Git, issue trackers, ADRs, and release notes.

## Choose an adoption path

### Minimal

Use the minimal profile for a small or mature repository. Start with project context, the skill reference, and the next step.

### Standard

Use the standard profile for active, complex, multi-language, or multi-agent repositories.

### Gradual

For most existing projects:

1. Bootstrap safely.
2. Fill project context and verified commands.
3. Define the active milestone, task, and next step.
4. Add current risks, dependencies, and invariants.
5. Start impact, acceptance, and evidence records on the next real task.

## Bootstrap

```bash
python -m pip install getdone-dev

getdone init \
  --project-root /path/to/repository \
  --skills-root ~/.getdone/skill-pack \
  --profile standard
```

Review and commit the generated `.agent/` directory separately from application changes.

## Populate records in this order

1. `.agent/project-context.md` — current purpose, users, boundaries, stack, constraints, and non-goals.
2. `.agent/command-reference.md` — only commands that have been verified.
3. `.agent/roadmap.md` and the active milestone — current and near-term outcomes.
4. `.agent/current/task.md` and `.agent/current/next-step.md` — the actual work boundary.
5. `.agent/invariants.md` — only durable truths with enforcement and review triggers.
6. Tracking records — current risks, blockers, and dependencies only.

Do not fabricate historical acceptance evidence. Begin evidence-backed operation on the next real task.

## Validate

```bash
getdone validate \
  --project-root /path/to/repository \
  --skills-root ~/.getdone/skill-pack

getdone doctor \
  --project-root /path/to/repository \
  --skills-root ~/.getdone/skill-pack
```

## ChatGPT-assisted adoption

Create a ChatGPT Project for the repository when persistent discussion context is useful. Upload the bootstrapped `.agent/` templates and selected current project documentation.

Generate the planning prompt:

```bash
getdone planning-prompt --mode project
```

Keep suggestions provisional until approval. After approval, have ChatGPT return complete records using the GetDone file-block protocol. Apply them to the repository, review the diff, and validate locally.

## Avoid migrating

- every closed issue or sprint;
- full Git history;
- resolved risks;
- superseded plans;
- speculative implementation details;
- duplicate architecture prose.

For the detailed checklist and completion criteria, see the repository guide: `docs/adopting-existing-project.md`.
