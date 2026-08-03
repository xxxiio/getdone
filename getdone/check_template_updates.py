#!/usr/bin/env python3
"""Print a non-destructive project-template migration plan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from getdone.markdown_merge import format_merge_suggestion
    from getdone.template_updates import inspect_template_updates
except ModuleNotFoundError:  # Direct execution from the tooling directory.
    from markdown_merge import format_merge_suggestion
    from template_updates import inspect_template_updates


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check project-local bootstrap templates without modifying project files."
    )
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--skills-root", type=Path)
    parser.add_argument("--profile")
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Print unified diffs for non-current files.",
    )
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
        results = inspect_template_updates(
            args.project_root,
            skills_root=args.skills_root,
            profile=args.profile,
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps([item.as_dict() for item in results], indent=2))
    else:
        for item in results:
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
            if args.diff and item.diff:
                print(item.diff, end="" if item.diff.endswith("\n") else "\n")
        actionable = sum(item.status != "current" for item in results)
        print(f"summary: {len(results)} managed file(s), {actionable} action or review item(s)")
        print("no project files were modified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
