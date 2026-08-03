---
id: standard.core.engineering
version: 1.2.0
status: stable
---

# Core Engineering Standard

## Rules

| Area | Required rule |
|---|---|
| Scope | Change only what is needed for the stated acceptance criteria. Record unrelated findings as TODOs. Apply YAGNI: do not build speculative flexibility. |
| Simplicity | Apply KISS: prefer the simplest design that preserves correctness, safety, and changeability. Avoid cleverness that increases explanation or test cost. |
| Structure | Apply Single responsibility and High cohesion: keep behaviour with the data and invariants it governs, and split only independently changing lifecycle, policy, I/O, or formatting concerns. Use Low coupling, explicit contracts, and dependency direction at real boundaries; apply Dependency inversion when domain policy owns the abstraction. Tell, do not ask and follow the Law of Demeter when an object can enforce its own invariant. |
| Reuse and patterns | Apply DRY to duplicated knowledge, rules, and invariants—not merely similar syntax. When adding common infrastructure, search `registry/reuse-catalogue.json`; reuse only when semantics, lifecycle, and ownership match. Introduce a pattern only for demonstrated variation or lifecycle complexity; direct code is preferred when simpler. |
| Errors | Use typed or distinguishable failures at boundaries. Preserve causal context, define recovery ownership, and do not leak secrets. |
| State | Minimise shared mutable state. Make transitions, invariants, idempotency, and concurrency ownership explicit. |
| Tests | Test stable observable behaviour. A bug fix needs regression evidence; a refactor needs characterisation evidence when coverage is weak. |
| Documentation | Update user, API, configuration, migration, or operational guidance in the same change when behaviour changes. |
| Context | Load canonical documents by reference. Do not duplicate shared rules in plans, adapters, or reports. |

## Review triggers

Perform a maintainability review when changed code has any of these signals:

- Function: more than 50 logical lines, complexity above 15, nesting above four,
  more than seven parameters, or mixed domain/I/O/formatting responsibilities.
- Type: more than 20 methods, more than seven direct dependencies, or multiple
  independent reasons to change.
- File: normal source above 500 lines or tests above 800 lines.
- Module: circular dependency, broad `utils` ownership, cross-layer imports, or an
  unrelated public API.
- Dependency: deep call chains, feature envy, duplicated business rules, or a domain
  layer importing infrastructure details.
- Change: new global state, hidden runtime dependency, broad reflection, or a pattern
  without a second real variation or explicit boundary need.

## Required response

1. Name the triggered concern and the principle at risk.
2. Identify independently changing responsibilities, duplicated knowledge, or the
   dependency boundary.
3. Consider guard clauses, extraction, composition, a value object, a domain method,
   an explicit interface, or a strategy.
4. Keep cohesive code intact when splitting would reduce clarity, correctness, or
   performance.
5. Run affected tests after any structural change and record why the revised boundary
   is easier to reason about.

## Exceptions

A trigger may remain when the completion report records the threshold, why the code is
cohesive, why decomposition is worse, and the test or benchmark evidence protecting it.
Generated code is exempt when clearly identified and reproducible. Principles are guides to
better design, not reasons to create unnecessary layers or abstractions.

## Evidence

Record the applicable project commands, outcomes, skipped-check reasons, and distinction
between pre-existing and introduced failures in the evidence manifest.
