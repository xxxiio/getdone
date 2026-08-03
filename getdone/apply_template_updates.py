#!/usr/bin/env python3
"""Apply explicitly authorised safe bootstrap-template migration actions."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from getdone.markdown_merge import format_merge_suggestion
    from getdone.template_updates import (
        RenderedTemplate,
        TemplateUpdate,
        inspect_template_updates,
        render_profile_templates,
    )
except ModuleNotFoundError:  # Direct execution from the tooling directory.
    from markdown_merge import format_merge_suggestion
    from template_updates import (
        RenderedTemplate,
        TemplateUpdate,
        inspect_template_updates,
        render_profile_templates,
    )


@dataclass(frozen=True)
class TemplateMigrationResult:
    profile: str
    planned: tuple[TemplateUpdate, ...]
    added: tuple[Path, ...]
    replaced: tuple[Path, ...]
    skipped: tuple[Path, ...]
    dry_run: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "profile": self.profile,
            "planned": [item.as_dict() for item in self.planned],
            "added": [path.as_posix() for path in self.added],
            "replaced": [path.as_posix() for path in self.replaced],
            "skipped": [path.as_posix() for path in self.skipped],
            "dry_run": self.dry_run,
        }


def _defer_profile_reference(
    item: TemplateUpdate,
    *,
    pending_additions: bool,
    apply_additions: bool,
    should_replace: bool,
) -> bool:
    return (
        should_replace
        and item.path == Path(".agent/skills-reference.md")
        and pending_additions
        and not apply_additions
    )


def _write_template(
    project_root: Path,
    item: TemplateUpdate,
    rendered: dict[Path, RenderedTemplate],
) -> None:
    template = rendered[item.path]
    destination = project_root / item.path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(template.content, encoding="utf-8")
    shutil.copymode(template.source_path, destination)


def _authorised_action(
    item: TemplateUpdate,
    *,
    apply_additions: bool,
    apply_replacements: bool,
) -> str | None:
    if item.safe_to_add and apply_additions:
        return "add"
    if item.safe_to_replace and apply_replacements:
        return "replace"
    return None


def _apply_plan(
    project_root: Path,
    planned: tuple[TemplateUpdate, ...],
    rendered: dict[Path, RenderedTemplate],
    *,
    apply_additions: bool,
    apply_replacements: bool,
) -> tuple[tuple[Path, ...], tuple[Path, ...], tuple[Path, ...]]:
    added: list[Path] = []
    replaced: list[Path] = []
    skipped: list[Path] = []
    pending_additions = any(item.safe_to_add for item in planned)

    for item in planned:
        action = _authorised_action(
            item,
            apply_additions=apply_additions,
            apply_replacements=apply_replacements,
        )
        if _defer_profile_reference(
            item,
            pending_additions=pending_additions,
            apply_additions=apply_additions,
            should_replace=action == "replace",
        ):
            skipped.append(item.path)
            continue
        if action is None:
            if item.status != "current":
                skipped.append(item.path)
            continue
        _write_template(project_root, item, rendered)
        (added if action == "add" else replaced).append(item.path)

    return tuple(added), tuple(replaced), tuple(skipped)


def apply_template_updates(
    project_root: Path,
    *,
    skills_root: Path | None = None,
    profile: str | None = None,
    apply_additions: bool = False,
    apply_replacements: bool = False,
) -> TemplateMigrationResult:
    """Apply only the separately authorised safe migration categories."""

    project_root = project_root.resolve()
    selected_profile, rendered = render_profile_templates(
        project_root,
        skills_root=skills_root,
        profile=profile,
    )
    planned = inspect_template_updates(
        project_root,
        skills_root=skills_root,
        profile=profile,
    )
    added, replaced, skipped = _apply_plan(
        project_root,
        planned,
        rendered,
        apply_additions=apply_additions,
        apply_replacements=apply_replacements,
    )
    return TemplateMigrationResult(
        selected_profile,
        planned,
        added,
        replaced,
        skipped,
        not apply_additions and not apply_replacements,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Plan or apply safe project-template migrations. The default is a read-only dry run."
        )
    )
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--skills-root", type=Path)
    parser.add_argument("--profile")
    parser.add_argument(
        "--apply-additions",
        action="store_true",
        help="Create profile files that are currently missing.",
    )
    parser.add_argument(
        "--apply-replacements",
        action="store_true",
        help="Replace only verified-unmodified files with newer managed templates.",
    )
    parser.add_argument("--no-diff", action="store_true")
    parser.add_argument(
        "--sections",
        action="store_true",
        help="Print read-only section-aware suggestions for modified Markdown files.",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = apply_template_updates(
            args.project_root,
            skills_root=args.skills_root,
            profile=args.profile,
            apply_additions=args.apply_additions,
            apply_replacements=args.apply_replacements,
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps(result.as_dict(), indent=2))
        return 0

    for item in result.planned:
        if item.safe_to_add:
            safety = "safe-add"
        elif item.safe_to_replace:
            safety = "safe-replace"
        elif item.status == "current":
            safety = "-"
        else:
            safety = "review"
        print(
            f"{item.status:18} {safety:12} {item.path.as_posix()} "
            f"({item.installed_version or '-'} -> {item.available_version or '-'})"
        )
        if args.sections and item.merge_suggestion is not None:
            print(format_merge_suggestion(item.merge_suggestion))
        if item.diff and not args.no_diff:
            print(item.diff, end="" if item.diff.endswith("\n") else "\n")

    mode = "dry-run" if result.dry_run else "apply"
    print(
        f"summary: mode={mode}, {len(result.added)} added, "
        f"{len(result.replaced)} replaced, {len(result.skipped)} skipped"
    )
    if result.dry_run:
        print("no project files were modified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
