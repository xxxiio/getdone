# Frozen v1 Public Contracts

The machine-readable freeze is `skill/contracts/public-contracts.json`. During the `1.x` release line,
changes to these surfaces follow `skill/policies/registry-compatibility.md` and semantic compatibility
rules rather than ad hoc replacement.

## Frozen surfaces

- Console command names.
- Exit-code classes: `0` success, `1` validation or operational failure, and `2` command usage
  failure.
- Bootstrap profile names and versions.
- Agent adapter contract version.
- Public JSON schema versions listed in the manifest, including project-record
  contract schema version 1.
- Supported Python and operating-system matrix.

The controlled record status values, section order, identifier formats, and schema
version are public project-state contracts. Template wording may improve compatibly, but
invalidating existing filled records requires migration guidance.

Command output wording is not a stable machine interface unless a command emits a published JSON
schema. Human-readable output may improve without a major release.

## Release-candidate rule

From `v1.0.0-rc.6` until `v1.0.0`, changes to a frozen surface are permitted only to correct a
rollout blocker. Such a correction must update the contract manifest, compatibility notes, tests,
and release notes together.

## Support window

The initial supported runtime is Python 3.11–3.13 on the latest GitHub-hosted Ubuntu, macOS, and
Windows environments. The canonical Markdown content is platform-neutral; the Python matrix
covers the distributed getdone.
