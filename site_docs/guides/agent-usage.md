---
title: "Using GetDone with coding agents"
description: "Set up GetDone for Codex and ChatGPT and use standard implementation, planning, and review prompts."
tags: ["guide", "agents", "codex", "chatgpt"]
---

# Using GetDone with coding agents

GetDone is a workflow and engineering-guidance layer around a coding agent. Bootstrap
creates project state once; task and project are workflow modes that only determine which
existing records the agent reads and writes. GetDone does not replace repository
exploration or implementation judgment.

## Responsibility boundary

| Component | Responsibility |
|---|---|
| Coding agent | Understand the request, inspect the repository, decide which source files matter, implement, test, and validate |
| GetDone wheel | Execute deterministic guidance routing, inspection, doctor, validation, and project-record commands |
| GetDone skill pack | Provide generic workflows, standards, policies, and acceptance guidance |
| `.project-agent/` | Provide durable repository-specific engineering guidance |
| `.agent/` | Store mutable GetDone/project execution state |

`--changed-path` means a known or anticipated affected path. The coding agent identifies
these paths after enough repository exploration to understand the likely scope. GetDone
uses them only to route workflow and project guidance.

## Install for Codex or another local coding agent

Use the wheel and skill pack from the same GetDone release.

```bash
python -m venv .getdone-venv
source .getdone-venv/bin/activate

python -m pip install getdone_dev-1.1.0-py3-none-any.whl
mkdir -p .getdone-runtime
unzip getdone-skill-pack-1.1.0.zip -d .getdone-runtime

export GETDONE_SKILLS_ROOT="$PWD/.getdone-runtime"

getdone --version
getdone doctor --project-root .
```

Windows PowerShell:

```powershell
python -m venv .getdone-venv
.getdone-venv\Scripts\Activate.ps1

python -m pip install .\getdone_dev-1.1.0-py3-none-any.whl
New-Item -ItemType Directory -Force .getdone-runtime | Out-Null
Expand-Archive .\getdone-skill-pack-1.1.0.zip .getdone-runtime

$env:GETDONE_SKILLS_ROOT = "$PWD\.getdone-runtime"

getdone --version
getdone doctor --project-root .
```

The runtime does not need to be committed to the application repository. A user-local
or centrally managed installation is usually cleaner. The consuming repository keeps
its own `.project-agent/` when repository-specific guidance is required.

## Choose the workflow mode

**Task workflow** is for one bounded request. Read only relevant stable project facts,
selected guidance, and historically relevant journal entries. Write the implementation,
validation evidence, durable journal history, and durable decisions when warranted.
Normally leave roadmap, current-task, plans, status, handoff, and next-step records
untouched.

**Project workflow** is for an ongoing goal spanning multiple tasks or sessions. Use the
same implementation guidance and journal history, plus the applicable current, planning,
evidence, status, reporting, and continuation records. Maintain
`.agent/current/next-step.md` separately from the journal.

## Codex task workflow

Codex should inspect the repository normally before asking GetDone for guidance. Once it
understands the likely scope, it passes the known or anticipated affected paths to
GetDone.

Recommended prompt:

> Use GetDone in task workflow for this bounded change. Independently inspect the
> repository and decide which source files are relevant. Once you understand the likely
> affected area, run `getdone guidance` with the appropriate task class,
> `--project-root .`, and the known or anticipated affected paths. Follow the returned
> generic and `.project-agent` guidance, implement and validate the change, then journal
> the completed work and durable findings. Do not create or update continuation state.
> Do not load the full journal unless prior work is specifically relevant.

## Codex project workflow

Recommended prompt:

> Use GetDone in project workflow for this ongoing development goal. Maintain the existing
> bootstrapped project state across iterations. Independently inspect the repository, use
> `getdone guidance` for each bounded implementation task, follow applicable
> `.project-agent` guidance, validate the work, journal completed work and durable
> decisions, and keep applicable current/planning/next-step records accurate for
> continuation.

Typical loop:

```text
user request
    ↓
agent explores repository
    ↓
agent identifies likely affected paths
    ↓
getdone guidance
    ↓
agent reads selected workflow + project guidance
    ↓
agent continues exploration and implementation
    ↓
project tests / lint / build
    ↓
GetDone validation / doctor checks
```

Example:

```bash
getdone guidance \
  --task-class feature \
  --project-root . \
  --changed-path applications/example/lib/settings/page.dart \
  --changed-path packages/design_system/lib/theme/theme.dart
```

The returned documents are engineering guidance. They are not a whitelist of source
files and do not replace the coding agent's working context.

## ChatGPT planning workflow

For a normal ChatGPT conversation, do not upload the wheel merely to provide guidance.
The wheel is executable tooling.

Generate a project-planning prompt locally:

```bash
getdone planning-prompt --mode project
```

Or an execution-planning prompt:

```bash
getdone planning-prompt --mode execution
```

Copy the generated prompt into ChatGPT and provide the project information it asks for.

Recommended ChatGPT instruction:

> Use the supplied GetDone planning guidance as the process contract. Help me refine the
> plan and identify missing decisions, risks, dependencies, validation, and acceptance
> evidence. Do not assume access to repository files unless I attach or connect them.

## ChatGPT implementation or review workflow

If ChatGPT is only a conversation surface, resolve the applicable guidance locally and
provide it together with the relevant diff, files, or connected repository context.

If ChatGPT is running in a coding environment that can execute local commands and access
the repository, use the same wheel + skill-pack setup as Codex and use the Codex-style
implementation prompt.

## Common use cases

| Use case | Coding agent role | GetDone role |
|---|---|---|
| Feature implementation | Explore, design, code, test | Route feature workflow and applicable standards/project guidance |
| Bug fix | Reproduce, diagnose, patch, test | Route defect workflow and required evidence |
| Refactor | Determine safe scope and invariants | Route refactor workflow and project constraints |
| Polyglot change | Discover affected implementation areas | Compose language standards from affected paths |
| Project planning | Discuss goals and milestones | Generate a structured project-planning prompt |
| Execution planning | Break a milestone into work | Generate an execution-planning prompt |
| Pull-request review | Review code and evidence | Supply applicable workflow/project quality criteria |
| CI | Execute deterministic checks | Validate project records, composition, and project-agent structure |

## Inspect project-specific guidance

When `.project-agent/` exists:

```bash
getdone project-agent validate --project-root .
getdone project-agent inspect \
  --project-root . \
  --changed-path applications/example/lib/settings/page.dart
```

`inspect` explains why project guidance was selected. It is not a source-file selector.

## Finish coding work

Run the repository's own tests, static analysis, lint, builds, and platform-specific
checks first. Then run the applicable GetDone checks:

```bash
getdone project-agent validate --project-root .
getdone doctor --project-root .
```

In task workflow, finish by writing durable journal history without creating a next-step
obligation. In project workflow, journal the same history and separately maintain the
current/evidence/status/next-step records required for continuation.

If the project uses bootstrapped `.agent/` records, run the project-record validation
required by the selected workflow.

## Preview the GetDone documentation

GetDone configures Zensical's local preview on `localhost:8001` to reduce collisions
with application/API servers that commonly use port `8000`.

```bash
zensical serve
```

You can override the address explicitly:

```bash
zensical serve --dev-addr localhost:8010
```

If the browser returns raw JSON such as `{"detail":"Not Found"}`, check which process
owns that port. A Zensical documentation page should render as HTML, not as that API
response.
