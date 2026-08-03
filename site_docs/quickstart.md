# Ten-Minute Quickstart

This is the recommended v1 adoption path: pin the shared skills repository as a Git submodule and
keep mutable project state in `.agent/`.

## 1. Add and pin the shared repository

```bash
git submodule add <approved-skills-repository-url> .getdone
git -C .getdone checkout v1.0.0
```

Treat `.getdone/` as read-only during ordinary application development.

## 2. Install the tooling

From the consuming project's Python environment:

```bash
python -m pip install getdone-dev
```

The wheel or editable package contains tooling only. Canonical guidance remains in
`.getdone/`.

## 3. Bootstrap project-owned state

```bash
getdone init \
  --project-root . \
  --skills-root .getdone \
  --skills-reference .getdone \
  --profile standard
```

This creates project-owned files under `.agent/` and a bootstrap-managed `AGENTS.md`. It does not
write live project state into `.getdone/`.

## 4. Install only the adapter you use

Codex already uses `AGENTS.md`. Other examples:

```bash
getdone-install-adapter \
  --project-root . \
  --skills-root .getdone \
  --adapter claude
```

```bash
getdone-install-adapter \
  --project-root . \
  --skills-root .getdone \
  --adapter cursor
```

Existing project-owned adapter files are preserved unless overwrite is explicit.

## 5. Verify the pinned composition

```bash
getdone-lock \
  --project-root . \
  --skills-root .getdone
```

Do this before agent work and after changing the shared checkout.

## 6. Select the minimum task context

Classify the task explicitly, then request canonical paths:

```bash
getdone context \
  --repository-root .getdone \
  --task-class feature \
  --language python
```

Load the returned documents rather than the entire repository. Conditional policies are loaded
only when their stated trigger applies.

## 7. Validate controlled records and project state

When `.agent/` records were created or materially changed:

```bash
getdone records \
  --project-root . \
  --skills-root .getdone
```

Then run full project-state validation:

```bash
getdone validate \
  --project-root . \
  --skills-root .getdone
```

Run the consuming project's formatter, linter, build, and tests separately using the commands
recorded in `.agent/command-reference.md`.

## Alternative: adjacent checkout

For environments that do not permit submodules, keep a pinned checkout at a stable path and pass
that path through `--skills-root` and `--skills-reference`. See [Distribution and installation
models](distribution.md).

## Product-only alternative

A centrally managed environment may extract the standalone skill-pack archive instead of
checking out the full source repository. Install the tooling wheel separately and pass the
extracted directory through `--skills-root`. The skill pack contains no tests, benchmarks,
rollout fixtures, or maintainer documentation.
