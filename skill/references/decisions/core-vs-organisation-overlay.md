# Core Contribution versus Organisation Overlay

## Decision

Place guidance in the core repository only when it is broadly reusable, non-confidential, agent-neutral, and maintainable as a shared public contract. Place organisation-specific policies, internal platforms, compliance conventions, and proprietary component contracts in a namespace-owned overlay.

## Prefer a core contribution when

- multiple unrelated organisations or projects face the same problem;
- the guidance does not reveal internal architecture or policy;
- identifiers and semantics can remain stable for general consumers;
- maintainers can support compatibility across agents and languages.

## Prefer an organisation overlay when

- the guidance names internal systems, teams, controls, or deployment rules;
- ownership and lifecycle belong to one organisation;
- the contract must evolve independently from the core release;
- access should be limited to authorised users.

## Avoid

Do not fork the core registry merely to add internal entries. Do not use an overlay to shadow core IDs, weaken safety requirements, or store mutable project state.
