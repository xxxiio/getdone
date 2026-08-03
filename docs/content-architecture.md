# Content Architecture

## Product boundary

`skill/` is the complete read-only agent product. A core registry entry, workflow,
standard, gate, policy, schema, adapter, bootstrap source, or worked example must live
under that directory. Tooling, tests, benchmarks, rollout evidence, maintainer notes, and
release machinery remain outside it.

The standalone skill-pack archive contains only:

```text
VERSION
skill/**
```

This allows an installed tooling wheel to operate against a small controlled content
checkout without exposing repository-development files as instructions.

## Loading model

One-time startup reads project instructions, project-local state, the composition lock,
`skill/START-HERE.md`, and the router. Recurring task execution then loads the smallest
operational set selected by task class and language.

| Task class | Recurring documents |
|---|---:|
| Feature | 6 |
| Bug fix | 6 |
| Refactoring | 6 |
| Investigation | 5 |

A normal six-document set contains the general workflow, one task workflow, core and
language standards, and core and task acceptance gates. Policies and references are
conditional. Agents must not preload all patterns, component guides, policies, schemas,
templates, or unrelated language material.

## Document types

### Procedure

A procedure is executable and must contain:

- when to use and not use it;
- required inputs;
- ordered steps;
- decision points;
- required evidence;
- stop conditions;
- completion criteria.

### Standard

A standard must contain:

- enforceable rules;
- observable review triggers;
- the response required when a trigger occurs;
- acceptable exceptions;
- evidence needed for review.

### Acceptance gate

A gate must distinguish pass, waiver, not-applicable, not-run, and failure based on
recorded evidence. It must not use subjective phrases such as “good quality” without an
observable condition.

### Policy

A policy states its trigger, ordered required action, evidence, and exceptions. Policies
are loaded only when the trigger applies.

### Reference

A reference supports a design decision after a trigger. It may explain alternatives and
examples but cannot silently add a mandatory workflow step. Registry discovery is
advisory.

### Template and schema

Templates create project-owned structure; they do not contain live project state.
Schemas define machine contracts and are loaded by tooling rather than normal task
context.

## Consolidation rule

Documents that are selected together for nearly every task should be consolidated unless
separation enables measurable omission. A proposed split must show at least one recurring
case that can skip the new document. A proposed merge must preserve independent routing
or lifecycle needs.

## Quality test

A canonical document is good enough when two competent agents would choose broadly the
same actions, evidence, and completion point. Repository validation checks structure;
rollout dogfood checks that the resulting set remains usable.

## Project-owned record contracts

Bootstrap templates are not free-form outlines. Their structure and lifecycle are governed
by `skill/contracts/project-records.md` and `skill/contracts/project-records.json`. The
record contract is conditional context: load it when creating, migrating, or materially
updating `.agent/` records, not for ordinary implementation tasks.
