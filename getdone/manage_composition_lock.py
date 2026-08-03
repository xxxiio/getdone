#!/usr/bin/env python3
"""Check, plan, or explicitly write a project-local skills composition lock."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from getdone.composition_lock import (
        LOCK_PATH,
        LockFinding,
        assess_lock,
        locked_overlay_paths,
        write_lockfile,
    )
    from getdone.frontmatter import parse_frontmatter
    from getdone.initialise_project import repository_root
except ModuleNotFoundError as exc:  # Direct execution from the tooling directory.
    if exc.name not in {
        "getdone",
        "getdone.composition_lock",
        "getdone.frontmatter",
        "getdone.initialise_project",
    }:
        raise
    from composition_lock import (
        LOCK_PATH,
        LockFinding,
        assess_lock,
        locked_overlay_paths,
        write_lockfile,
    )
    from frontmatter import parse_frontmatter
    from initialise_project import repository_root


def _project_profile(project_root: Path) -> str:
    reference = project_root / ".agent/skills-reference.md"
    document = parse_frontmatter(reference.read_text(encoding="utf-8"))
    profile = document.data.get("bootstrap_profile")
    if not isinstance(profile, str) or not profile:
        raise ValueError(f"{reference}: bootstrap_profile is missing")
    return profile


def _effective_overlays(
    project_root: Path,
    skills_root: Path,
    requested: list[Path],
) -> tuple[Path, ...]:
    if requested:
        return tuple(requested)
    lock_path = project_root / LOCK_PATH
    if not lock_path.is_file():
        return ()
    return locked_overlay_paths(project_root, skills_root)


def _print_assessment(status: str, findings: tuple[LockFinding, ...]) -> None:
    print(f"composition: {status}")
    for finding in findings:
        print(f"- {finding.component}: {finding.status} ({finding.detail})")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check, plan, or write the project-local skills composition lock."
    )
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--skills-root", type=Path, default=repository_root())
    parser.add_argument("--profile")
    parser.add_argument("--overlay", type=Path, action="append", default=[])
    parser.add_argument("--skills-reference")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--plan", action="store_true", help="Report compatibility without writing.")
    action.add_argument("--write", action="store_true", help="Explicitly create or replace the lock.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    project_root = args.project_root.resolve()
    skills_root = args.skills_root.resolve()
    try:
        overlays = _effective_overlays(project_root, skills_root, args.overlay)
        if args.write:
            profile = args.profile or _project_profile(project_root)
            path, status = write_lockfile(
                project_root,
                skills_root,
                profile,
                overlay_paths=overlays,
                skills_reference=args.skills_reference,
                overwrite=True,
            )
            print(f"{status}: {path}")
            return 0
        assessment = assess_lock(
            project_root,
            skills_root,
            overlay_paths=overlays if args.overlay else None,
            profile_name=args.profile,
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _print_assessment(assessment.status, assessment.findings)
    if args.plan:
        return 0
    return 0 if assessment.is_current else 1


if __name__ == "__main__":
    raise SystemExit(main())
