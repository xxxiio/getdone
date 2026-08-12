#!/usr/bin/env python3
"""Initialise the canonical full project-local agent state."""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

try:
    from getdone.composition_lock import write_lockfile
    from getdone.frontmatter import add_template_digest
    from getdone.profiles import collect_profile_templates, load_profiles, resolve_profile
except ModuleNotFoundError as exc:  # Direct execution from the tooling directory.
    if exc.name not in {
        "getdone",
        "getdone.composition_lock",
        "getdone.frontmatter",
        "getdone.profiles",
    }:
        raise
    from composition_lock import write_lockfile
    from frontmatter import add_template_digest
    from profiles import collect_profile_templates, load_profiles, resolve_profile

TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".txt"}
BOOTSTRAP_PROFILE = "standard"


@dataclass(frozen=True)
class InitResult:
    created: tuple[Path, ...]
    skipped: tuple[Path, ...]


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_skills_version(root: Path) -> str:
    return (root / "VERSION").read_text(encoding="utf-8").strip()


def render_text(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def _render_values(
    project_root: Path,
    skills_root: Path,
    profile: str,
    profile_version: str,
    profile_lineage: tuple[str, ...],
    project_name: str | None,
    skills_reference: str | None,
) -> dict[str, str]:
    return {
        "PROJECT_NAME": project_name or project_root.name,
        "SKILLS_REPOSITORY": skills_reference or str(skills_root),
        "SKILLS_VERSION": load_skills_version(skills_root),
        "GENERATED_AT": date.today().isoformat(),
        "BOOTSTRAP_PROFILE": profile,
        "BOOTSTRAP_PROFILE_VERSION": profile_version,
        "BOOTSTRAP_PROFILE_LINEAGE": " -> ".join(profile_lineage),
    }


def _write_templates(
    project_root: Path,
    templates: dict[Path, Path],
    values: dict[str, str],
    *,
    overwrite: bool,
) -> tuple[list[Path], list[Path]]:
    created: list[Path] = []
    skipped: list[Path] = []
    for relative, source_path in sorted(templates.items()):
        destination = project_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and not overwrite:
            skipped.append(relative)
            continue
        if source_path.suffix.lower() in TEXT_SUFFIXES:
            rendered = render_text(source_path.read_text(encoding="utf-8"), values)
            destination.write_text(add_template_digest(rendered), encoding="utf-8")
            shutil.copymode(source_path, destination)
        else:
            shutil.copy2(source_path, destination)
        created.append(relative)
    return created, skipped


def initialise_project(
    project_root: Path,
    profile: str,
    *,
    overwrite: bool = False,
    skills_root: Path | None = None,
    project_name: str | None = None,
    skills_reference: str | None = None,
    overlay_paths: tuple[Path, ...] = (),
) -> InitResult:
    skills_root = (skills_root or repository_root()).resolve()
    profiles = load_profiles(skills_root)
    resolved = resolve_profile(profiles, profile)
    templates = collect_profile_templates(skills_root, resolved, profiles=profiles)
    project_root = project_root.resolve()
    project_root.mkdir(parents=True, exist_ok=True)
    values = _render_values(
        project_root,
        skills_root,
        profile,
        resolved.version,
        resolved.lineage,
        project_name,
        skills_reference,
    )
    created, skipped = _write_templates(
        project_root, templates, values, overwrite=overwrite
    )
    lock_path, lock_status = write_lockfile(
        project_root,
        skills_root,
        profile,
        overlay_paths=overlay_paths,
        skills_reference=skills_reference or str(skills_root),
        overwrite=overwrite,
    )
    (skipped if lock_status == "skipped" else created).append(lock_path)
    return InitResult(tuple(created), tuple(skipped))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create the canonical full project-local .agent state."
    )
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--skills-root",
        type=Path,
        help="Path to the shared skills repository. Defaults to the source checkout.",
    )
    parser.add_argument("--project-name")
    parser.add_argument(
        "--overlay",
        type=Path,
        action="append",
        default=[],
        help="Organisation catalogue overlay to pin in the project lock. Repeatable.",
    )
    parser.add_argument(
        "--skills-reference",
        help="Portable path or URL recorded in generated project metadata.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing project files. Use carefully; project state is project-owned.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = initialise_project(
            args.project_root,
            BOOTSTRAP_PROFILE,
            overwrite=args.overwrite,
            skills_root=args.skills_root,
            project_name=args.project_name,
            skills_reference=args.skills_reference,
            overlay_paths=tuple(args.overlay),
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for path in result.created:
        print(f"created: {path}")
    for path in result.skipped:
        print(f"skipped existing: {path}")
    print(f"summary: {len(result.created)} created, {len(result.skipped)} skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
