# Release Process

## Preconditions

- Repository validation passes.
- Front-matter, manifest, and controlled project-record validation passes.
- All tests pass.
- Direct-script and installed-wheel smoke tests pass.
- `VERSION` is the sole maintained release value; `pyproject.toml` derives its package version from it, and the changelog has a matching entry.
- `skill/contracts/public-contracts.json` matches the packaged commands and schemas.
- The committed rollout matrix passes without drift.
- The release commit contains no live consuming-project `.agent/` state.

## Build outputs

A release should contain:

- Python source distribution and wheel.
- Standalone skill-pack ZIP containing only `VERSION` and `skill/`.
- Python tooling wheel.
- SHA-256 checksum file covering every published artifact.

The wheel is tooling only and must be distributed with access to either a matching full checkout or extracted skill pack.

## Tag policy

Published releases should use an annotated, maintainer-signed tag:

```bash
git tag -s v<version> -m "GetDone <version>"
git verify-tag v<version>
```

When a signing key is unavailable, an annotated local tag may be created for development artefacts, but the release must be reported as unsigned and must not be represented as a verified published release.

## Verification

Consumers should verify the signed tag when a public Git remote is available, then verify
the release artifact checksums:

```bash
git verify-tag v<version>
sha256sum --check getdone-<version>-SHA256SUMS.txt
```

The tag workflow uploads the wheel, source distribution, standalone skill pack, and checksum
file to the GitHub release only after PyPI upload succeeds. It does not create a Git bundle;
consumers obtain complete history through the published repository remote.

## Stable-release policy

`1.0.0` establishes the public v1 compatibility boundary. Subsequent releases must preserve or
deliberately migrate its public contracts. The supported CI matrix is Python 3.11–3.13 on Ubuntu,
macOS, and Windows, with C++ dogfood on Ubuntu.

## One-command local preflight

Install the release extras and run the complete local gate before creating a tag:

```bash
python -m pip install -e '.[release]'
python development/scripts/check_release.py --repository-root .
```

The command validates release metadata and generated content, runs the repository tests,
builds and checks distributions, and installs the wheel into an isolated target for CLI smoke
testing. Hosted release CI repeats these checks and always requires the strict Zensical and
Twine paths before publication.

## Automated PyPI publication

The repository publishes the Python distribution through
`.github/workflows/publish-pypi.yml`.

The workflow is triggered only by a pushed `v*` tag. Before building or publishing, it
fetches `origin/main` and requires the tag commit to equal the current `main` HEAD. A tag
created from another branch, an older main commit, or an unmerged release branch fails before
credentials are used.

Create a protected GitHub Environment named `pypi`, then configure this environment secret:

- `PYPI_API_TOKEN`: a PyPI API token authorised to upload the `getdone-dev` distribution.

Restrict the `pypi` environment to protected release tags and configure a repository ruleset
that protects the `v*` tag namespace. Optional required reviewers provide an additional manual
release boundary.

The workflow passes the token to Twine as `TWINE_PASSWORD` with the fixed username
`__token__`. Do not store a PyPI username, password, or token in the repository.

The workflow also verifies that the pushed tag exactly matches `VERSION`, builds a source
distribution, wheel, and standalone skill pack, generates SHA-256 checksums, uploads the
Python distributions to PyPI, and creates a GitHub release containing all artifacts.

Release sequence:

1. Merge the release commit to `main`.
2. Confirm required CI checks pass on that exact commit.
3. Create the release tag from the current `main` HEAD.
4. Push only the tag: `git push origin v<version>`.
5. Review the `publish-pypi` workflow and its uploaded distribution artefact.
6. Confirm the new version is available from PyPI before creating other release announcements.

GitHub tag filters cannot directly express a source branch. The explicit commit equality check
is therefore the authoritative guard that limits publication to tags created at `main` HEAD.

## Automate GitHub repository setup

After the repository exists and `gh auth status` succeeds, a maintainer can configure the
release environment and GitHub Pages from the source checkout:

```bash
python development/scripts/configure_github_release.py --repository OWNER/getdone
```

To create the protected `pypi` environment, enable GitHub Pages workflow mode, and store the
PyPI token without writing it to disk:

```bash
python development/scripts/configure_github_release.py \
  --repository OWNER/getdone \
  --set-pypi-token < /secure/path/to/pypi-token.txt
```

Delete the temporary token file immediately after the command succeeds. Interactive use is also
supported: omit the redirection, paste the token, then send end-of-file.

The helper cannot safely choose repository governance for the maintainer. Configure these items
in GitHub after it runs:

- protect `main`;
- protect the `v*` tag namespace;
- optionally require approval for the `pypi` environment;
- restrict who may create release tags.
