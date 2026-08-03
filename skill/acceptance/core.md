---
id: acceptance.core
version: 1.0.0
status: stable
---
# Core Acceptance Gate

## Gate statuses
Use exactly `pass`, `fail`, `not-applicable`, `waived`, or `not-run`.

## Pass conditions
- The stated objective and observable acceptance criteria are met.
- Scope is controlled; unrelated changes and generated artefacts are absent.
- Required tests fail before the fix or feature when applicable, then pass afterward.
- Applicable formatter, linter, static-analysis, type, build, package, security, and
  performance checks have recorded outcomes.
- Error, dependency, compatibility, data, and security impacts were considered.
- Complexity review triggers from `standards/core.md` were resolved or documented.
- Behavioural, configuration, migration, API, or operational documentation is current.
- Changed public APIs have accurate language-appropriate documentation comments, or a documented project-permitted exception.
- Relevant generated API documentation and documentation examples build or run successfully when supported by the project.
- Remaining TODOs, risks, blockers, decisions, and one next step are stored project-locally.

## Required evidence
Record the changed behaviour, test names or commands, health-check commands and outcomes,
skipped checks with reasons, documentation changed, known limitations, and gate statuses.

## Waiver conditions
A waiver names the failed or skipped gate, reason, risk, mitigation, owner, expiry or
removal condition, and follow-up TODO. A waiver cannot conceal a known data-loss,
security, or destructive-update blocker.

## Failure conditions
The change is not accepted when required behaviour is untested, a relevant check fails
because of the change, documentation materially disagrees with behaviour, project-owned
state was overwritten without authority, or completion is claimed with an unresolved
blocking gate.
