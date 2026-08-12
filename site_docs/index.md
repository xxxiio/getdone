---
title: "GetDone"
description: "Deterministic, evidence-backed workflows and project records for coding agents."
tags: ["overview"]
---

# GetDone

GetDone is a read-only skill pack plus a small tooling package for running structured, evidence-backed software-development work with coding agents.

It provides:

- deterministic workflows for features, defects, migrations, incidents, refactoring, performance, documentation, and architecture;
- language standards for Python, Rust, C++, Dart/Flutter, q/kdb+, and TypeScript;
- controlled project records for tasks, milestones, next steps, impact, evidence, risks, decisions, and handoffs;
- guidance selection that normally loads no more than six relevant guidance documents;
- validators that prevent unsupported completion claims and stale generated catalogues.

## Start here

1. Read the [quick start](quickstart.md).
2. Understand the [development lifecycle](concepts/development-lifecycle.md).
3. Browse the [skills catalogue](catalogue/index.md).
4. Read [Using GetDone with coding agents](guides/agent-usage.md) for Codex and ChatGPT workflows.
5. Use the [CLI reference](reference/cli.md) for exact commands.

## Source-of-truth model

The shared `skill/` directory is immutable product guidance. A consuming project owns mutable state under `.agent/`. Generated catalogue pages describe authoritative registries but never replace them.
