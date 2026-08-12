# Distribution and Installation Models

The skills content and the Python tooling are separate distribution concerns:

- The full source repository contains `skill/` plus development tooling, tests, benchmarks, and rollout evidence.
- The standalone skill-pack archive contains only `VERSION` and `skill/`.
- The Python wheel contains commands only; it operates against either a full checkout or an extracted skill pack.

A consuming project should pin the resolved composition in `.agent/skills.lock.json` and control the shared checkout version it uses.

## Recommended coding-agent bundle

For Codex, CI, or another coding-agent environment that can execute local commands,
take these artifacts from the **same GetDone release**:

1. `getdone_dev-<version>-py3-none-any.whl` — executable CLI/tooling;
2. `getdone-skill-pack-<version>.zip` — generic workflows, standards, and policies;
3. `getdone-<version>-SHA256SUMS.txt` — integrity verification.

The wheel and skill pack are complementary. The wheel does not embed the canonical
workflow content, while the skill pack does not install the `getdone` command. Keep
their versions aligned.

A consuming repository may additionally contain `.project-agent/` for its own durable
engineering guidance. That repository-specific content is separate from the GetDone
release artifacts.

A normal ChatGPT planning conversation does not need the wheel uploaded into the chat.
Generate or resolve the relevant GetDone prompt/guidance locally, then supply that text
to ChatGPT. If ChatGPT is running in a coding environment that can execute commands and
access the repository, use the same wheel + skill-pack model as Codex.

See [Using GetDone with coding agents](guides/agent-usage.md) for concrete workflows and prompts.

## Supported models

| Model | Shared content location | Tooling | Best fit |
|---|---|---|---|
| Adjacent or global checkout | A stable local path | Source scripts or wheel | Individual developers and internal environments |
| Git submodule | Inside the consuming repository | Source scripts or wheel | Projects requiring an exact reviewed skills commit |
| Vendored snapshot | Copied read-only directory | Source scripts or wheel | Restricted or offline environments |
| Wheel plus checkout | Any accessible checkout | Installed console commands | Centrally managed developer tooling |

## Adjacent or global checkout

Keep the shared repository outside the consuming project and record a portable path when possible:

```bash
getdone-init \
  --project-root /work/example \
  --skills-root /opt/getdone \
  --skills-reference /opt/getdone \
  --profile standard
```

The checkout should be pinned to an approved tag or commit rather than silently following an unreviewed branch.

## Git submodule

A submodule gives the consuming project an explicit skills commit:

```bash
git submodule add <approved-repository-url> .getdone
git -C .getdone checkout v1.0.0

python .getdone/getdone/initialise_project.py \
  --project-root . \
  --skills-root .getdone \
  --skills-reference .getdone \
  --profile standard
```

The `.getdone/` directory is shared content and should remain read-only during ordinary application work. The project-owned `.agent/` directory remains mutable.

## Vendored snapshot

A vendored snapshot is acceptable when network access, submodules, or global installations are unavailable. Preserve the upstream version and source commit in the consuming project's dependency records. Do not edit the vendored copy during application work; contribute reusable changes back to the canonical skills repository.


## Standalone skill pack

Use the product-only archive when consuming environments do not need repository tests,
benchmarks, rollout fixtures, or maintainer documentation:

```bash
unzip getdone-skill-pack-1.0.0.zip -d /opt/getdone
python -m pip install getdone_dev-1.0.0-py3-none-any.whl
getdone-lock --project-root /work/example --skills-root /opt/getdone
```

The archive contains `VERSION` and `skill/` only.

## Installed wheel plus shared checkout

Install the tooling wheel, then point commands at the shared content:

```bash
python -m pip install getdone_dev-1.0.0-py3-none-any.whl

getdone-init \
  --project-root /work/example \
  --skills-root /opt/getdone \
  --profile standard

getdone-validate-records \
  --project-root /work/example \
  --skills-root /opt/getdone

getdone-validate-project \
  --project-root /work/example \
  --skills-root /opt/getdone
```

Installing the wheel alone is insufficient because workflows and acceptance gates remain in `skill/`; provide a full checkout or extracted skill pack. Run `getdone-lock` before agent work to verify the checkout matches the project lock.

## Catalogue search

The installed tooling can search a separately located shared checkout:

```bash
getdone-search \
  --repository-root /opt/getdone \
  --query "transient failure backoff" \
  --json
```

The command is read-only. The wheel still does not embed the canonical registry or Markdown content.

## Adapter installation

After bootstrapping, install only the agent-specific files needed by the project:

```bash
getdone-install-adapter \
  --project-root /work/example \
  --skills-root /opt/getdone \
  --adapter claude
```

Codex uses the bootstrap-managed `AGENTS.md`. ChatGPT uses conversational or workspace references and requires no additional project file. See [Agent adapter contracts](catalogue/adapters.md).

## Updating

1. Point `getdone-lock --plan` at the candidate shared checkout.
2. Review compatibility and composition changes.
3. Update or replace the shared checkout deliberately.
4. Run `getdone-check-updates` and review the plan.
5. Apply safe additions and verified replacements independently.
6. Review modified project-owned Markdown with section-aware evidence.
7. Write the reviewed lock with `getdone-lock --write`.
8. Run `getdone-validate-project`.
9. Commit project-local migrations separately from shared-repository updates where practical.

## Trust and integrity

Before adopting a release:

- Verify the selected commit or annotated tag.
- Prefer a maintainer-signed tag when the distribution channel supports signature verification.
- Verify published SHA-256 checksums for archives and wheels.
- Review changes to workflows, policies, acceptance gates, schemas, and bootstrap templates.
- Do not execute tooling from an untrusted checkout merely because the Markdown appears safe.

See [Release process](maintainers/repository-development.md) for the signing and verification policy.
