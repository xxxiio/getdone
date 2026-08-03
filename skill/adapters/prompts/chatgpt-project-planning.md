# ChatGPT Project Planning Prompt

Use GetDone's `workflow.general.project-planning` workflow.

Begin in discovery mode. Keep a compact decision ledger with four categories: agreed, tentative, unknown, and deferred. Ask only questions that materially affect outcome, MVP scope, constraints, milestone order, or risk. Do not present suggestions as approved decisions.

When I explicitly approve the direction, enter commitment mode and produce the applicable controlled records:

- `.agent/plans/PROJECT-PLAN-####.md`
- `.agent/project-context.md`
- `.agent/roadmap.md`
- `.agent/milestones/MILESTONE-####.md`
- `.agent/tracking/risks.md`
- `.agent/tracking/dependencies.md`
- `.agent/invariants.md` when durable invariants are identified
- `.agent/decisions/ADR-####.md` only when the ADR threshold is met
- `.agent/current/next-step.md`

When you cannot write files directly, use this exact delivery format for every approved artefact:

```text
BEGIN GETDONE FILE: <target .agent path>
<complete Markdown content>
END GETDONE FILE
```

Generate only records supported by the approved discussion. Preserve existing project-owned content when it is provided. End with exactly one first deterministic step. State clearly whether files were actually written or only generated for the user to apply.
