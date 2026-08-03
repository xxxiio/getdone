# Adopting GetDone in an Existing Project

This guide applies to an existing package, library, service, application, monorepo, data platform, or other software repository.

A **software project** is the repository being governed by GetDone. A **ChatGPT Project** is an optional ChatGPT workspace that can retain chats, uploaded files, and project-specific instructions. They are related, but they are not the same thing. The repository remains the authoritative source of truth.

## Migration principle

Adopt GetDone from the project's current state forward. Do not reconstruct every historical sprint, issue, decision, or implementation detail.

The migration should establish:

- stable project context;
- verified development commands;
- the active milestone and current task;
- current risks, blockers, and dependencies;
- durable invariants;
- exactly one next deterministic step.

Historical material should remain in Git, issue trackers, existing ADRs, and release notes unless it is still necessary to understand or govern current work.

## Choose an adoption depth

### Minimal adoption

Use the minimal profile when the repository is small, mature, or needs only a reliable agent entry point.

Start with:

- `.agent/project-context.md`
- `.agent/skills-reference.md`
- `.agent/current/next-step.md`

### Standard adoption

Use the standard profile for active, complex, multi-language, or multi-agent projects. It adds roadmap, milestone, task, evidence, impact, invariant, planning, tracking, and reporting records.

### Gradual adoption

For most existing repositories, gradual adoption is safest:

1. Bootstrap without overwriting project files.
2. Populate project context and commands.
3. Define the active milestone, task, and next step.
4. Add current risks, dependencies, and invariants.
5. Begin using change-impact, acceptance, and evidence records on the next real task.
6. Add execution plans only when a milestone genuinely needs multiple slices.

Do not block productive work until every optional record is complete.

## 1. Install GetDone and obtain the skill pack

Install the tooling:

```bash
python -m pip install get-done
```

Keep a version-pinned, read-only copy of the product skill pack in a stable location, for example:

```text
~/.getdone/skill-pack/
```

The Python package provides the CLI and validators. The extracted skill pack provides the versioned workflows, standards, acceptance gates, contracts, and templates.

## 2. Bootstrap the repository

For a standard adoption:

```bash
getdone init \
  --project-root /path/to/repository \
  --skills-root ~/.getdone/skill-pack \
  --profile standard
```

Use `--profile minimal` for lightweight adoption.

Bootstrap must not silently replace existing project-owned files. Review the generated `.agent/` directory before committing it.

Create a dedicated adoption commit:

```bash
git add .agent
git commit -m "adopt GetDone project records"
```

This commit establishes a visible governance boundary without mixing it with application changes.

## 3. Inventory existing sources of truth

Before filling templates, identify where the project currently records authoritative information.

Typical sources include:

- `README.md` and contributor guides;
- architecture documentation and ADRs;
- build configuration and CI workflows;
- issue tracker milestones;
- current planning documents;
- release documentation;
- source and test layout;
- operational runbooks.

Record which source is authoritative for each subject. Do not copy all content into `.agent/`; summarise only what future work needs.

## 4. Populate stable project context

Fill `.agent/project-context.md` with current facts:

- project purpose and intended users;
- primary use cases;
- repository and system boundaries;
- technology stack;
- supported platforms and environments;
- important constraints;
- stable architecture;
- explicit non-goals;
- external systems and ownership boundaries.

Keep this record concise. It is frequently loaded and should not become another general README.

## 5. Record verified commands

Populate `.agent/command-reference.md` with commands that have actually been run successfully.

At minimum, record applicable commands for:

- installation;
- formatting and linting;
- type checking;
- unit and integration tests;
- full quality validation;
- packaging or build output;
- documentation build.

Do not infer commands from tool names or stale documentation. If a command is not verified, label it unresolved instead of presenting it as canonical.

## 6. Establish the current planning baseline

Convert only the planning state that still affects current work.

Populate:

- `.agent/roadmap.md`;
- the active milestone under `.agent/milestones/`;
- `.agent/current/task.md`;
- `.agent/current/next-step.md`.

Use this planning horizon:

- **Current milestone:** detailed outcome and binary exit criteria.
- **Next milestone:** clear outcome and dependencies.
- **Later milestones:** outcome-level only.

Do not import every completed phase. Retain completed milestones only when they explain current architecture or compatibility obligations.

The next deterministic step must be one reviewable action with concrete outputs and validation. Avoid phrases such as “continue development” or “improve quality”.

## 7. Capture durable invariants

Populate `.agent/invariants.md` only with truths future changes must preserve.

Examples:

- domain code does not import infrastructure adapters;
- persisted events remain backward compatible;
- timestamps are timezone-aware;
- the same decision logic is used across execution modes;
- public APIs do not expose mutable internal state.

Each invariant should have a stable ID, an enforcement mechanism, and a review trigger. General coding advice belongs in GetDone standards, not the project invariant register.

## 8. Migrate decisions selectively

Keep existing ADRs in their current authoritative location. Add or reference only durable decisions that future agents must consult, such as:

- architecture boundaries;
- persistence formats;
- public API strategies;
- significant technology choices;
- compatibility commitments;
- expensive or difficult-to-reverse decisions.

Do not create retrospective ADRs for every historical implementation choice.

## 9. Record current risks and dependencies

Populate the tracking records with current items only:

- `.agent/tracking/risks.md`
- `.agent/tracking/blockers.md`
- `.agent/tracking/dependencies.md`

Resolved history should remain in the existing issue tracker or Git history. Every active item should state its impact, owner or resolution path, and review or unblock condition.

## 10. Introduce evidence on the next real task

Do not fabricate evidence for historical work. On the next implementation task:

1. classify `.agent/current/change-impact.md`;
2. define binary acceptance criteria;
3. run the required validation tiers;
4. record actual results in `.agent/current/evidence.md`;
5. update the current task and next step;
6. create a completion or handoff report when applicable.

This creates a trustworthy evidence boundary from adoption onward.

## 11. Validate the adopted state

Run:

```bash
getdone validate \
  --project-root /path/to/repository \
  --skills-root ~/.getdone/skill-pack
```

Then run diagnostics:

```bash
getdone doctor \
  --project-root /path/to/repository \
  --skills-root ~/.getdone/skill-pack
```

Fix structural failures before treating the records as authoritative. A failed migration should remain reviewable and reversible rather than being forced through with broad waivers.

## ChatGPT-assisted migration

A ChatGPT Project is optional. It is useful as a persistent workspace for one software repository.

Provide ChatGPT with:

- the newly bootstrapped `.agent/` templates;
- the current README and contributor guide;
- architecture documentation and important ADRs;
- current roadmap or issue-milestone summaries;
- relevant release and operational documentation.

Generate the canonical prompt:

```bash
getdone planning-prompt --mode project
```

Then ask ChatGPT to analyse current state without inventing history. Keep all proposals tentative until explicitly approved. After approval, ChatGPT should return complete files using the GetDone file-block protocol.

Apply the returned files to the repository, review the diff, and run `getdone validate`. An uploaded or generated copy is not authoritative until it is applied to the repository and accepted through the project's normal review process.

## What not to migrate

Avoid importing:

- every closed issue or previous sprint;
- full Git history;
- resolved risks and blockers;
- superseded plans;
- old completion reports;
- speculative long-range implementation detail;
- duplicated architecture prose;
- vague backlog ideas without approval.

The goal is a concise operational baseline, not a second archive of the project's past.

## Completion criteria

Migration is complete when:

- the repository has a pinned skill-pack reference;
- stable project context and verified commands are recorded;
- the active milestone and current task are unambiguous;
- current risks, dependencies, and invariants are represented where relevant;
- exactly one next deterministic step is ready;
- `getdone validate` passes or every remaining failure is explicitly understood;
- future work will produce evidence from the adoption boundary onward.
