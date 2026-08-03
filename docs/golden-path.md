# Golden Path: Complete One Small Feature

This tutorial shows the intended GetDone lifecycle without loading the whole skill pack.

## 1. Install and diagnose

```bash
python -m pip install getdone-dev
getdone --version
getdone doctor --project-root . --skills-root /path/to/getdone-skill-pack
```

The PyPI distribution provides the CLI. The shared skill pack remains a separately pinned,
read-only input and may be a checkout, submodule, or extracted product-only archive.

## 2. Bootstrap project state

```bash
getdone init \
  --project-root . \
  --skills-root /path/to/getdone-skill-pack \
  --skills-reference /path/to/getdone-skill-pack \
  --profile standard
```

Fill in `.agent/project-context.md`, `.agent/command-reference.md`, and the active roadmap,
task, impact, and next-step records. Replace guided placeholders before changing an
operational record from draft or proposed to ready or active.

## 3. Select only the required guidance

```bash
getdone context \
  --skills-root /path/to/getdone-skill-pack \
  --task-class feature \
  --language python
```

Read only the returned documents plus project-owned records relevant to the task.

## 4. Declare the change boundary

In `.agent/current/change-impact.md`, classify every impact dimension as `yes`, `no`, or
`unknown`. A `yes` activates its named specialist gate. Record what must not change in the
active task.

## 5. Implement one reviewable slice

Write a failing observable test, confirm the failure, implement the smallest useful change,
then run the project-defined test tier. Do not expand into a second objective.

The sample under `examples/golden-path/` demonstrates a tiny Python feature and its tests.

## 6. Record evidence

Update `.agent/current/acceptance.md` and `.agent/current/evidence.md`. A passed criterion
must cite a command result or concrete artefact. A skipped check needs a reason and impact.

## 7. Validate and close the iteration

```bash
getdone records --project-root . --skills-root /path/to/getdone-skill-pack
getdone validate --project-root . --skills-root /path/to/getdone-skill-pack
```

Then create the task-completion report, append a journal entry, update project status, and
replace `current/next-step.md` with exactly one next deterministic objective.
