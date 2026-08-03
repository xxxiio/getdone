# Bootstrap Profile Inheritance

Profiles may extend one or more parent profiles. Resolution is deterministic and parent-first; child sources override parent files with the same relative path.

## Manifest example

```json
{
  "schema_version": 1,
  "profiles": {
    "minimal": {
      "version": "1.3.0",
      "description": "Minimal project continuity state",
      "source": "skill/bootstrap/templates/minimal"
    },
    "standard": {
      "version": "1.3.0",
      "description": "Full project planning and reporting state",
      "extends": ["minimal"],
      "source": "skill/bootstrap/templates/standard"
    },
    "organisation-python": {
      "version": "1.0.0",
      "description": "Organisation defaults layered over standard",
      "extends": ["standard"],
      "source": "skill/bootstrap/templates/organisation-python"
    }
  }
}
```

A profile may contain only `extends` when it is an aggregate profile with no additional files.

## Resolution rules

1. Resolve parents in the order listed.
2. Resolve each ancestor once in diamond-shaped inheritance.
3. Apply the selected profile last.
4. Let a later layer replace an earlier file only at the same relative path.
5. Reject unknown parents and inheritance cycles.
6. Record the selected profile, version, and resolved lineage in `.agent/skills-reference.md`.

## Versioning

The profile version describes the assembled profile contract. Individual files retain independent template versions. Increment the profile version when the effective set, overlay order, or required semantics change.

When a child intentionally provides a richer variant of a parent template, give the child template a newer version so profile migration can identify a safe replacement of an unmodified parent-generated file.
