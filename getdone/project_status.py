"""Read-only summaries of project-owned GetDone records."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from getdone.frontmatter import parse_frontmatter
from getdone.project_records import RecordFinding, validate_project_records


@dataclass(frozen=True)
class RecordSummary:
    """The stable identity and lifecycle state of one controlled record."""

    path: str
    identifier: str | None
    status: str | None
    milestone_id: str | None


@dataclass(frozen=True)
class ProjectStatusSummary:
    """A compact, evidence-backed view of the project's current operating state."""

    current_milestone: str | None
    current_task: RecordSummary | None
    next_step: RecordSummary | None
    acceptance: RecordSummary | None
    evidence: RecordSummary | None
    record_findings: tuple[RecordFinding, ...]

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["record_findings"] = [
            {"path": finding.path.as_posix(), "message": finding.message}
            for finding in self.record_findings
        ]
        return payload


def _read_record(project_root: Path, relative: Path) -> RecordSummary | None:
    path = project_root / relative
    if not path.is_file():
        return None
    document = parse_frontmatter(path.read_text(encoding="utf-8"))
    identifier = document.data.get("id")
    status = document.data.get("status")
    milestone_id = document.data.get("milestone_id")
    return RecordSummary(
        relative.as_posix(),
        identifier if isinstance(identifier, str) else None,
        status if isinstance(status, str) else None,
        milestone_id if isinstance(milestone_id, str) else None,
    )


def project_status_summary(project_root: Path, skills_root: Path) -> ProjectStatusSummary:
    """Summarise authoritative current records without writing project state."""

    project_root = project_root.resolve()
    roadmap = _read_record(project_root, Path(".agent/roadmap.md"))
    current_milestone: str | None = None
    roadmap_path = project_root / ".agent/roadmap.md"
    if roadmap_path.is_file():
        document = parse_frontmatter(roadmap_path.read_text(encoding="utf-8"))
        value = document.data.get("current_milestone")
        current_milestone = value if isinstance(value, str) else None
    del roadmap
    return ProjectStatusSummary(
        current_milestone=current_milestone,
        current_task=_read_record(project_root, Path(".agent/current/task.md")),
        next_step=_read_record(project_root, Path(".agent/current/next-step.md")),
        acceptance=_read_record(project_root, Path(".agent/current/acceptance.md")),
        evidence=_read_record(project_root, Path(".agent/current/evidence.md")),
        record_findings=tuple(validate_project_records(project_root, skills_root.resolve())),
    )


def render_project_status(summary: ProjectStatusSummary) -> str:
    """Render a concise human-readable status report from a summary."""

    def line(label: str, record: RecordSummary | None) -> str:
        if record is None:
            return f"- {label}: unavailable"
        identity = record.identifier or "no ID"
        milestone = f"; milestone={record.milestone_id}" if record.milestone_id else ""
        return f"- {label}: {identity}; status={record.status or 'unknown'}{milestone}"

    lines = ["# GetDone Project Status", "", "## Current state"]
    lines.append(f"- Current milestone: {summary.current_milestone or 'none'}")
    lines.extend(
        (
            line("Current task", summary.current_task),
            line("Next step", summary.next_step),
            line("Acceptance", summary.acceptance),
            line("Evidence", summary.evidence),
            "",
            "## Record validation",
        )
    )
    if summary.record_findings:
        lines.extend(
            f"- {finding.path.as_posix()}: {finding.message}"
            for finding in summary.record_findings
        )
    else:
        lines.append("- Controlled records are structurally consistent.")
    return "\n".join(lines) + "\n"
