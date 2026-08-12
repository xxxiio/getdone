from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from getdone.initialise_project import initialise_project
from getdone.project_records import (
    main as validate_records_main,
    validate_profile_record_templates,
    validate_project_records,
    validate_record_text,
)


ROOT = Path(__file__).resolve().parents[1]


class ProjectRecordContractTests(unittest.TestCase):
    def test_all_profile_record_templates_satisfy_contracts(self) -> None:
        self.assertEqual(validate_profile_record_templates(ROOT), [])

    def test_recorded_journal_has_no_continuation_requirement(self) -> None:
        text = """---
template: journal-entry
template_version: 2.1.0
project_owned: true
record_contract: journal-entry
record_schema_version: 1
status: recorded
date: "2026-08-12"
task_id: null
---

# Journal Entry: 2026-08-12 — Complete bounded task

## Context

One bounded task requested by the user.

## Work completed

- Completed the requested implementation.

## Decisions made

- Preserved the existing public API.

## Files or components changed

- `src/example.py`

## Validation performed

- `python -m pytest tests/test_example.py` passed.

## Problems encountered

- None.

## Remaining work

- None.

## New TODOs

- None.

## Risks or blockers

- None.
"""
        self.assertEqual(validate_record_text(text, ROOT), [])

    def test_fresh_standard_project_has_valid_draft_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            initialise_project(project, "standard", skills_root=ROOT)

            findings = validate_project_records(project, ROOT)

            self.assertEqual(findings, [])

    def test_ready_next_step_requires_executable_content(self) -> None:
        template = (
            ROOT
            / "skill/bootstrap/templates/minimal/.agent/current/next-step.md"
        ).read_text(encoding="utf-8")
        ready = template.replace("status: proposed", "status: ready")

        errors = validate_record_text(ready, ROOT)

        self.assertTrue(any("Objective" in error and "placeholder" in error for error in errors))
        self.assertTrue(any("Ordered actions" in error for error in errors))
        self.assertTrue(any("Acceptance criteria" in error for error in errors))

    def test_next_step_rejects_unknown_status_and_unordered_actions(self) -> None:
        text = _next_step("MILESTONE-0003", ("EC-002",))
        text = text.replace("status: ready", "status: running")
        text = text.replace(
            "1. Define the record contracts.\n"
            "2. Validate the managed templates.\n"
            "3. Integrate validation into project health checks.",
            "- Define the record contracts.\n"
            "- Validate the managed templates.\n"
            "- Integrate validation into project health checks.",
        )

        errors = validate_record_text(text, ROOT)

        self.assertTrue(any("status" in error and "running" in error for error in errors))
        self.assertTrue(
            any(
                "Ordered actions" in error and "ordered list" in error
                for error in errors
            )
        )

    def test_passed_acceptance_report_requires_passing_gate_rows(self) -> None:
        template = (
            ROOT
            / "skill/bootstrap/templates/standard/.agent/current/acceptance.md"
        ).read_text(encoding="utf-8")
        passed = template.replace("status: draft", "status: passed")

        errors = validate_record_text(passed, ROOT)

        self.assertTrue(any("at least one gate result" in error for error in errors))

    def test_heading_order_is_contractual(self) -> None:
        template = (
            ROOT
            / "skill/bootstrap/templates/minimal/.agent/current/next-step.md"
        ).read_text(encoding="utf-8")
        reordered = template.replace(
            "## Preconditions\n\n",
            "## Inputs\n\n<!-- input -->\n\n## Preconditions\n\n",
            1,
        )

        errors = validate_record_text(reordered, ROOT)

        self.assertTrue(any("H2 headings" in error for error in errors))

    def test_roadmap_rejects_multiple_active_milestones(self) -> None:
        roadmap = _roadmap(
            milestones=(
                _milestone("MILESTONE-0001", "active", "EC-001"),
                _milestone("MILESTONE-0002", "active", "EC-002"),
            ),
            current="MILESTONE-0001",
        )

        errors = validate_record_text(roadmap, ROOT)

        self.assertTrue(any("at most one active milestone" in error for error in errors))

    def test_completed_milestone_requires_checked_criteria_and_evidence(self) -> None:
        block = _milestone("MILESTONE-0001", "completed", "EC-001")
        block = block.replace(
            "- EC-001: `python -m pytest tests/test_project_record_contracts.py`",
            "- EC-001: not available",
        )
        roadmap = _roadmap(milestones=(block,), current="null")

        errors = validate_record_text(roadmap, ROOT)

        self.assertTrue(any("EC-001 is unchecked" in error for error in errors))
        self.assertTrue(any("EC-001 has no evidence" in error for error in errors))

    def test_active_milestone_requires_completed_dependencies(self) -> None:
        first = _milestone("MILESTONE-0001", "ready", "EC-001")
        second = _milestone("MILESTONE-0002", "active", "EC-002").replace(
            "- **Depends on:** none",
            "- **Depends on:** MILESTONE-0001",
        )
        roadmap = _roadmap(
            milestones=(first, second),
            current="MILESTONE-0002",
        )

        errors = validate_record_text(roadmap, ROOT)

        self.assertTrue(any("dependency MILESTONE-0001" in error for error in errors))

    def test_roadmap_rejects_unknown_next_milestone(self) -> None:
        block = _milestone("MILESTONE-0001", "active", "EC-001").replace(
            "#### Next milestone\n\nnone",
            "#### Next milestone\n\nMILESTONE-9999",
        )
        roadmap = _roadmap(milestones=(block,), current="MILESTONE-0001")

        errors = validate_record_text(roadmap, ROOT)

        self.assertTrue(any("unknown next milestone MILESTONE-9999" in error for error in errors))

    def test_project_cross_references_next_step_to_roadmap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            initialise_project(project, "standard", skills_root=ROOT)
            roadmap_path = project / ".agent/roadmap.md"
            roadmap_path.write_text(
                _roadmap(
                    milestones=(
                        _milestone("MILESTONE-0001", "active", "EC-001"),
                    ),
                    current="MILESTONE-0001",
                ),
                encoding="utf-8",
            )
            next_step_path = project / ".agent/current/next-step.md"
            next_step_path.write_text(
                _next_step("MILESTONE-0001", ("EC-999",)),
                encoding="utf-8",
            )

            findings = validate_project_records(project, ROOT)

            self.assertTrue(
                any(
                    finding.path == Path(".agent/current/next-step.md")
                    and "EC-999" in finding.message
                    for finding in findings
                )
            )

    def test_active_task_must_match_the_current_roadmap_milestone(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            initialise_project(project, "standard", skills_root=ROOT)
            (project / ".agent/roadmap.md").write_text(
                _roadmap(
                    milestones=(
                        _milestone("MILESTONE-0001", "active", "EC-001"),
                        _milestone("MILESTONE-0002", "ready", "EC-002"),
                    ),
                    current="MILESTONE-0001",
                ),
                encoding="utf-8",
            )
            task_path = project / ".agent/current/task.md"
            task_path.write_text(
                task_path.read_text(encoding="utf-8")
                .replace("status: proposed", "status: active")
                .replace("milestone_id: null", "milestone_id: MILESTONE-0002"),
                encoding="utf-8",
            )

            findings = validate_project_records(project, ROOT)

            self.assertTrue(
                any(
                    finding.path == Path(".agent/current/task.md")
                    and "must match current roadmap milestone" in finding.message
                    for finding in findings
                )
            )

    def test_completed_task_requires_final_evidence_and_accepted_gates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            initialise_project(project, "standard", skills_root=ROOT)
            task_path = project / ".agent/current/task.md"
            task_path.write_text(
                task_path.read_text(encoding="utf-8").replace(
                    "status: proposed", "status: completed"
                ),
                encoding="utf-8",
            )

            findings = validate_project_records(project, ROOT)

            task_path = Path(".agent/current/task.md")
            messages = [finding.message for finding in findings if finding.path == task_path]
            self.assertTrue(any("passed or waived" in message for message in messages))
            self.assertTrue(any("final evidence manifest" in message for message in messages))


    def test_change_impact_rejects_unknown_status_and_missing_gate(self) -> None:
        text = _change_impact(
            rows=(
                ("public_api", "yes", "API compatibility and documentation", "acceptance/core"),
                ("concurrency", "maybe", "Concurrency safety", "none"),
            ),
            status="ready",
        )

        errors = validate_record_text(text, ROOT)

        self.assertTrue(any("invalid impact value 'maybe'" in error for error in errors))
        self.assertTrue(any("activated gate" in error for error in errors))

    def test_evidence_manifest_requires_evidence_for_passed_results(self) -> None:
        text = _evidence_manifest(
            acceptance_rows=(("AC-001", "pass", ""),),
            gate_rows=(("tests", "pass", "python -m pytest", ""),),
            status="final",
        )

        errors = validate_record_text(text, ROOT)

        self.assertTrue(any("AC-001" in error and "evidence" in error for error in errors))
        self.assertTrue(any("tests" in error and "result" in error for error in errors))

    def test_invariant_register_requires_stable_ids_and_controlled_status(self) -> None:
        text = _invariant_register(
            rows=(
                (
                    "BAD",
                    "Domain points inward",
                    "architecture",
                    "import check",
                    "boundary change",
                    "active-ish",
                ),
            ),
            status="current",
        )

        errors = validate_record_text(text, ROOT)

        self.assertTrue(any("invalid invariant ID" in error for error in errors))
        self.assertTrue(any("invalid invariant status" in error for error in errors))

    def test_fresh_standard_project_contains_structural_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            initialise_project(project, "standard", skills_root=ROOT)

            self.assertTrue((project / ".agent/current/change-impact.md").is_file())
            self.assertTrue((project / ".agent/current/evidence.md").is_file())
            self.assertTrue((project / ".agent/invariants.md").is_file())

    def test_validation_cli_accepts_fresh_project(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            initialise_project(project, "standard", skills_root=ROOT)

            code = validate_records_main(
                [
                    "--project-root",
                    str(project),
                    "--skills-root",
                    str(ROOT),
                ]
            )

            self.assertEqual(code, 0)

    def test_valid_filled_roadmap_and_next_step_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            initialise_project(project, "standard", skills_root=ROOT)
            (project / ".agent/roadmap.md").write_text(
                _roadmap(
                    milestones=(
                        _milestone("MILESTONE-0001", "active", "EC-001"),
                    ),
                    current="MILESTONE-0001",
                ),
                encoding="utf-8",
            )
            (project / ".agent/current/next-step.md").write_text(
                _next_step("MILESTONE-0001", ("EC-001",)),
                encoding="utf-8",
            )

            findings = validate_project_records(project, ROOT)

            next_step_findings = [
                finding
                for finding in findings
                if finding.path
                in {Path(".agent/roadmap.md"), Path(".agent/current/next-step.md")}
            ]
            self.assertEqual(next_step_findings, [])


def _milestone(identifier: str, status: str, exit_criterion: str) -> str:
    return f"""### {identifier} — Controlled project records

- **Status:** {status}
- **Outcome:** Project records are deterministic and validated.
- **Why now:** Loose templates are a rollout blocker.
- **Depends on:** none

#### Scope

- Record contracts and validation.

#### Non-goals

- New workflow categories.

#### Exit criteria

- [ ] {exit_criterion}: A filled record passes deterministic validation.

#### Evidence

- {exit_criterion}: `python -m pytest tests/test_project_record_contracts.py`

#### Next milestone

none
"""


def _roadmap(*, milestones: tuple[str, ...], current: str) -> str:
    return f"""---
template: roadmap
template_version: 2.0.0
project_owned: true
record_contract: roadmap
record_schema_version: 1
status: current
current_milestone: {current}
---
# Project Roadmap

## Product outcome

A supported skill pack with deterministic project records.

## Ordering principles

1. Fix rollout blockers before adding capabilities.

## Milestones

{''.join(milestones)}
## Deferred work

- Hosted registry support — reconsider after v1.0 adoption evidence.
"""


NEXT_STEP_BODY = """# Next Deterministic Step

## Objective

Implement deterministic validation for project records.

## Why this is next

It resolves a confirmed rollout blocker before v1.0.

## Preconditions

- The RC.2 baseline is restored.

## Inputs

- `skill/bootstrap/templates/`
- `skill/contracts/project-records.json`

## Ordered actions

1. Define the record contracts.
2. Validate the managed templates.
3. Integrate validation into project health checks.

## Expected outputs

- `getdone/project_records.py`
- Focused tests and migration documentation.

## Acceptance criteria

- [ ] NS-001: Invalid controlled statuses are rejected.
- [ ] NS-002: Roadmap and next-step references are consistent.

## Validation

```bash
python -m pytest tests/test_project_record_contracts.py
```

## Stop conditions

- Stop if migration would overwrite project-owned content.

## Out of scope

- New workflow categories or language standards.
"""


def _next_step(milestone: str, exit_criteria: tuple[str, ...]) -> str:
    criteria_yaml = "\n".join(f"  - {item}" for item in exit_criteria)
    frontmatter = f"""---
template: next-step
template_version: 3.0.0
project_owned: true
record_contract: next-step
record_schema_version: 1
id: NEXT-0042
status: ready
milestone_id: {milestone}
advances_exit_criteria:
{criteria_yaml}
---
"""
    return frontmatter + NEXT_STEP_BODY


def _change_impact(*, rows: tuple[tuple[str, str, str, str], ...], status: str) -> str:
    table = "\n".join(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows)
    return f"""---
template: change-impact
template_version: 1.0.0
project_owned: true
record_contract: change-impact
record_schema_version: 1
status: {status}
task_id: TASK-0001
---
# Change Impact Declaration

## Task

TASK-0001 — Controlled records.

## Impact classification

| Impact | Value | Reason | Activated gate |
|---|---|---|---|
{table}

## Assumptions and unknowns

- None.

## Required outputs

- Evidence manifest.

## Test tier

- Tier 2 — affected module tests.
"""


def _evidence_manifest(
    *,
    acceptance_rows: tuple[tuple[str, str, str], ...],
    gate_rows: tuple[tuple[str, str, str, str], ...],
    status: str,
) -> str:
    acceptance = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in acceptance_rows)
    gates = "\n".join(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in gate_rows)
    return f"""---
template: evidence-manifest
template_version: 1.0.0
project_owned: true
record_contract: evidence-manifest
record_schema_version: 1
status: {status}
task_id: TASK-0001
---
# Evidence Manifest

## Task

TASK-0001 — Controlled records.

## Acceptance evidence

| Criterion ID | Status | Evidence |
|---|---|---|
{acceptance}

## Quality gate evidence

| Gate | Status | Command or artefact | Result |
|---|---|---|---|
{gates}

## Checks not run

- None.

## Waivers

- None.

## Residual risk

- None recorded.
"""


def _invariant_register(
    *,
    rows: tuple[tuple[str, str, str, str, str, str], ...],
    status: str,
) -> str:
    table = "\n".join(
        f"| {a} | {b} | {c} | {d} | {e} | {f} |"
        for a, b, c, d, e, f in rows
    )
    return f"""---
template: invariant-register
template_version: 1.0.0
project_owned: true
record_contract: invariant-register
record_schema_version: 1
status: {status}
---
# System Invariants

## Invariants

| ID | Invariant | Scope | Enforcement | Review trigger | Status |
|---|---|---|---|---|---|
{table}
"""

    def test_ready_execution_plan_rejects_unknown_dependency_and_cycle(self) -> None:
        template = (
            ROOT
            / "skill/bootstrap/templates/standard/.agent/plans/EXECUTION-PLAN-TEMPLATE.md"
        ).read_text(encoding="utf-8")
        ready = template.replace("status: draft", "status: ready")
        ready = ready.replace("<Approved milestone outcome advanced by this plan.>", "Deliver the milestone")
        ready = ready.replace("<!-- Approved milestone outcome advanced by this plan. -->", "Deliver the milestone")
        ready = ready.replace("<!-- Why this work cannot honestly fit into one deterministic step. -->", "It requires two reviewable changes.")
        ready = ready.replace("- <Precondition>", "- Milestone is approved")
        ready = ready.replace("- <Assumption or unknown and its disposition>", "- No unresolved unknowns")
        ready = ready.replace("- **Depends on:** none", "- **Depends on:** SLICE-999")
        ready = ready.replace("- <Included work>", "- Add the contract")
        ready = ready.replace("- <Preserved behaviour>", "- Existing callers remain compatible")
        ready = ready.replace("<Binary condition>", "Contract tests pass")
        ready = ready.replace("- <Risk or stop condition>", "- Stop if compatibility fails")
        ready = ready.replace("<!-- One executable step linked to first_slice_id. -->", "Add the failing contract test.")

        errors = validate_record_text(ready, ROOT)

        self.assertTrue(any("unknown slice SLICE-999" in error for error in errors))

    def test_chatgpt_adapter_supports_approved_planning_artifacts(self) -> None:
        text = (ROOT / "skill/adapters/chatgpt.md").read_text(encoding="utf-8")

        self.assertIn("discovery mode", text)
        self.assertIn("target `.agent/` path", text)
        self.assertIn("user confirms", text)


if __name__ == "__main__":
    unittest.main()
