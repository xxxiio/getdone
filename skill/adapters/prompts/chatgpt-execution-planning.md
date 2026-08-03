# ChatGPT Execution Planning Prompt

Use GetDone's `workflow.general.execution-planning` workflow for one approved milestone.

Verify the milestone outcome and exit criteria before decomposition. Create stable `SLICE-NNN` outcomes with explicit dependencies, advanced exit criteria, scope, must-not-change behaviour, validation tier, binary acceptance criteria, integration order, and stop or rollback conditions. Do not guess low-level files, classes, or methods unless an approved contract requires them.

Present the decomposition for approval. After approval, produce:

- `.agent/plans/PLAN-####.md`
- `.agent/current/next-step.md`
- dependency, risk, or decision records only when materially changed

When you cannot write files directly, use this exact delivery format:

```text
BEGIN GETDONE FILE: <target .agent path>
<complete Markdown content>
END GETDONE FILE
```

Exactly one slice may be the first ready slice. State clearly whether files were actually written or only generated for the user to apply.
