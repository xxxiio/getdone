# Plugin System Boundary

## Intent

Support explicit extension points with versioned contracts, controlled discovery, isolation, and lifecycle management.

## Use when

- Independent teams or deployments need optional capabilities.
- Extension contracts are stable enough to version.
- Loading and trust boundaries can be controlled.

## Avoid when

- Only one implementation exists and internal composition is sufficient.
- Plugins would bypass ownership, security, or release controls.
- The contract changes faster than consumers can follow.

## Required contract

- Define discovery, compatibility, activation, and shutdown.
- Version public interfaces and capability negotiation.
- Limit plugin access to explicit host services.
- Record ownership and support expectations.

## Failure and lifecycle questions

- One plugin must not corrupt unrelated host state.
- Invalid or incompatible plugins fail with actionable diagnostics.
- Timeouts, resource limits, and isolation are defined where needed.

## Acceptance evidence

- Compatibility matrix
- Load and unload
- Isolation
- Invalid plugin diagnostics
- Host-service permissions

## Promotion rule

Promote an implementation into a shared component only when compatible semantics, ownership, and upgrade policy are demonstrated across real consumers. Similar-looking code alone is not sufficient.

See [Shared Component Checklist](component-checklist.md).
