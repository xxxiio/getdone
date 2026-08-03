---
title: "Project records"
description: "Authoritative mutable records maintained by a consuming project."
tags: ["concepts", "records"]
---

# Project records

The standard profile uses controlled Markdown records rather than unrestricted notes.

| Subject | Authoritative record |
|---|---|
| Current objective | `.agent/current/next-step.md` |
| Task scope and acceptance | `.agent/current/task.md` |
| Change risk classification | `.agent/current/change-impact.md` |
| Validation proof | `.agent/current/evidence.md` |
| Milestone ordering | `.agent/roadmap.md` and milestone records |
| Stable system truths | `.agent/invariants.md` |
| Current project health | `.agent/status/project-status.md` |
| Historical activity | `.agent/journal/` |
| Durable architectural choices | `.agent/decisions/` |

Validators enforce controlled statuses, stable IDs, exact sections, evidence requirements, and cross-record references. Historical reports do not override current records.
