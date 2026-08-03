# Supported Versions and Compatibility

## Runtime support

GetDone 1.x supports CPython 3.11, 3.12, and 3.13 on Linux, macOS, and Windows.
The documentation site is optional and uses the exact Zensical version pinned by the
`docs` extra.

## Public compatibility commitments

- Stable workflow, registry, and record-contract IDs are not reused within 1.x.
- Consecutive supported bootstrap-profile versions receive non-destructive migration guidance.
- Project-owned `.agent/` content is preserved unless overwrite is explicit.
- Breaking record-schema or CLI changes require a documented migration and a major version.

## Support window

The current minor release and the immediately previous minor release receive fixes for
blocking packaging, migration, security, and data-loss defects. Release candidates are
supported only until the next release candidate or final release supersedes them.

## Out of scope

GetDone does not guarantee support for end-of-life Python versions, unpinned development
snapshots, modified generated files, or projects that bypass migration and validation gates.
