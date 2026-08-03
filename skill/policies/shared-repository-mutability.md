---
id: policy.shared-repository-mutability
version: 1.0.0
status: stable
---
# Shared Repository Mutability

## Applies when
An agent uses this repository while working on another consuming project.

## Required action
1. Treat `skill/` as read-only product content.
2. Create plans, journals, milestones, decisions, validation results, and TODOs only in
   the consuming project's `.agent/` directory.
3. Render bootstrap templates into the consuming project; never store rendered project
   state in this repository.
4. Modify this repository only when the assigned task explicitly concerns the skills
   product or its development infrastructure.

## Required evidence
Project validation must show that mutable state exists only in the consuming project and
that no live `.agent/` directory was created in the shared repository.

## Exceptions
Repository-maintenance tasks may create temporary fixtures under `tests/`, `development/rollout/`, or
a temporary directory. They must not be presented as live consuming-project state.
