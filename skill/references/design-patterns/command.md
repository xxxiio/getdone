# Command

## Intent

Represent an action as data so execution, queuing, auditing, retries, or undo can be handled explicitly.

## Use when

- Actions cross an asynchronous, transactional, or audited boundary.
- Execution policy should be separate from request creation.

## Avoid when

- A direct function call is synchronous and sufficient.
- Command objects would only add boilerplate around local calls.

## Decision questions

- What concrete source of variation, lifecycle, or ownership does the pattern make explicit?
- Could a function, value object, enum, or direct dependency remain clearer?
- Does the pattern reduce the cost of testing and future change after its extra concepts are counted?
- Are public contracts and failure behaviour smaller and clearer than before?

## Evidence before adoption

- Name at least two real callers, implementations, operations, or transitions when the pattern depends on variation.
- Show the boundary in tests or a small worked example.
- Record why simpler alternatives were rejected when the added indirection is material.

## Tags

- Execution
- Messaging
- Audit

Patterns are decision aids, not architecture quotas.
