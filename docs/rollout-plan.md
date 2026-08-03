# v1.0 Rollout Plan

## Target

```text
v0.9.0      Measured context selection
v1.0.0-rc.2 Content architecture correction — complete locally
v1.0.0-rc.6 Controlled project records — complete locally
v1.0.0      Initial supported release
```

Milestone 10 is the final capability milestone before v1.0. Milestone 11 is release readiness,
not another feature-expansion phase.

## Pre-v1 stop rule

Do not add another workflow category, language, pattern entry, registry concept, adapter, or
automation before v1.0 unless representative dogfooding identifies its absence as a rollout
blocker.

A rollout blocker is limited to:

- Data-loss or destructive-update risk.
- Broken bootstrap, migration, lock, validation, or packaging behaviour.
- Non-reproducible guidance composition.
- A major incompatibility across supported agents or language ecosystems.
- Documentation insufficient for unaided adoption.
- Required context that materially harms successful task execution.

Cosmetic improvements and optional capabilities move to the post-v1 backlog.

## Milestone 11: release readiness — complete for local RC

1. Dogfood at least three representative consuming repositories.
2. Exercise at least two coding agents and two language ecosystems.
3. Complete feature, bug-fix, and refactoring tasks with recorded evidence.
4. Freeze schemas, CLI names, exit-code behaviour, profiles, and adapter contracts.
5. Validate clean bootstrap, existing-project adoption, upgrade, rollback, and modified-file safety.
6. Provide a ten-minute quickstart and one recommended installation path.
7. Run CI across supported Python versions and operating systems.
8. Configure a release remote and signing process when authorised credentials are available.
9. Publish an RC and fix rollout blockers only.

## v1.0 exit criteria

- The rollout matrix is complete and published.
- No known blocking data-loss or destructive-update issue exists.
- Packaged tooling passes bootstrap, lock, migration, search, selection, validation, and adapter
  smoke workflows.
- A new adopter can follow the quickstart without maintainer assistance.
- Public contracts are frozen under the compatibility policy.
- The RC passes the supported CI matrix.

## Post-v1 backlog

Additional languages, hosted registries, richer analytics, user interfaces, automatic merging,
and new workflow families are evaluated after rollout using measured adoption evidence.

## RC status

The executable rollout matrix, contract freeze, quickstart, and supported CI configuration are
complete. Public remote publication and signature verification remain external release operations.
Between the RC and v1.0, only rollout-blocking fixes are accepted.
