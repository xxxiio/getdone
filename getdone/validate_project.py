#!/usr/bin/env python3
"""Validate project-local agent state against a shared bootstrap profile."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from getdone.composition_lock import LOCK_PATH, assess_lock
    from getdone.initialise_project import repository_root
    from getdone.project_records import validate_project_records
    from getdone.template_updates import TemplateUpdate, inspect_template_updates
except ModuleNotFoundError as exc:  # Direct execution from the tooling directory.
    if exc.name not in {
        "getdone",
        "getdone.composition_lock",
        "getdone.initialise_project",
        "getdone.template_updates",
    }:
        raise
    from composition_lock import LOCK_PATH, assess_lock
    from initialise_project import repository_root
    from project_records import validate_project_records
    from template_updates import TemplateUpdate, inspect_template_updates


@dataclass(frozen=True)
class ProjectFinding:
    path: Path
    message: str


@dataclass(frozen=True)
class ProjectValidationReport:
    errors: tuple[ProjectFinding, ...]
    warnings: tuple[ProjectFinding, ...]
    managed_files: int
    composition_digest: str | None = None
    overlay_versions: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return not self.errors


_REQUIRED_PATHS = (
    Path("AGENTS.md"),
    Path(".agent/skills-reference.md"),
    LOCK_PATH,
    Path(".agent/project-context.md"),
    Path(".agent/current/next-step.md"),
)
_ERROR_STATUSES = {
    "missing",
    "unmanaged-source",
    "untracked",
    "template-mismatch",
    "invalid-version",
}
_WARNING_STATUSES = {"modified", "update-available", "ahead"}


def _required_path_errors(project_root: Path) -> list[ProjectFinding]:
    return [
        ProjectFinding(path, "required project-agent file is missing")
        for path in _REQUIRED_PATHS
        if not (project_root / path).is_file()
    ]


def _composition_validation(
    project_root: Path,
    skills_root: Path,
) -> tuple[list[ProjectFinding], str | None, tuple[str, ...]]:
    try:
        assessment = assess_lock(project_root, skills_root)
    except (OSError, ValueError) as exc:
        return [ProjectFinding(LOCK_PATH, str(exc))], None, ()
    errors = [
        ProjectFinding(
            LOCK_PATH,
            f"{finding.component}: {finding.status}: {finding.detail}",
        )
        for finding in assessment.findings
        if finding.status != "current"
    ]
    return errors, assessment.composition_digest, assessment.overlay_versions


def _classify_template_updates(
    updates: tuple[TemplateUpdate, ...],
) -> tuple[list[ProjectFinding], list[ProjectFinding]]:
    errors: list[ProjectFinding] = []
    warnings: list[ProjectFinding] = []
    for update in updates:
        finding = ProjectFinding(update.path, f"{update.status}: {update.reason}")
        if update.status in _ERROR_STATUSES:
            errors.append(finding)
        elif update.status in _WARNING_STATUSES:
            warnings.append(finding)
    return errors, warnings


def validate_project(
    project_root: Path,
    *,
    skills_root: Path | None = None,
    profile: str | None = None,
) -> ProjectValidationReport:
    project_root = project_root.resolve()
    skills_root = (skills_root or repository_root()).resolve()
    errors = _required_path_errors(project_root)
    if errors:
        return ProjectValidationReport(tuple(errors), (), 0)
    try:
        updates = inspect_template_updates(
            project_root, skills_root=skills_root, profile=profile
        )
    except (OSError, ValueError) as exc:
        finding = ProjectFinding(Path(".agent/skills-reference.md"), str(exc))
        return ProjectValidationReport((finding,), (), 0)
    lock_errors, digest, overlays = _composition_validation(project_root, skills_root)
    update_errors, warnings = _classify_template_updates(updates)
    record_errors = [
        ProjectFinding(finding.path, finding.message)
        for finding in validate_project_records(project_root, skills_root)
    ]
    errors.extend(lock_errors)
    errors.extend(update_errors)
    errors.extend(record_errors)
    return ProjectValidationReport(
        tuple(errors), tuple(warnings), len(updates), digest, overlays
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a consuming project's agent state.")
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--skills-root", type=Path)
    parser.add_argument("--profile")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = validate_project(
        args.project_root,
        skills_root=args.skills_root,
        profile=args.profile,
    )
    for finding in report.errors:
        print(f"error: {finding.path}: {finding.message}", file=sys.stderr)
    for finding in report.warnings:
        print(f"warning: {finding.path}: {finding.message}")
    if report.errors:
        print(f"validation failed: {len(report.errors)} error(s)", file=sys.stderr)
        return 1
    digest = report.composition_digest[:12] if report.composition_digest else "unavailable"
    overlays = ", ".join(report.overlay_versions) if report.overlay_versions else "none"
    print(
        f"validation passed: {report.managed_files} managed file(s), "
        f"{len(report.warnings)} warning(s); composition={digest}; overlays={overlays}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
