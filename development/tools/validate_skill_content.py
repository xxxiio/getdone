#!/usr/bin/env python3
"""Validate that canonical skill documents are operational rather than vague advice."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

try:
    from getdone.frontmatter import parse_frontmatter
except ModuleNotFoundError as exc:
    if exc.name not in {"getdone", "getdone.frontmatter"}:
        raise
    from frontmatter import parse_frontmatter

WORKFLOW_HEADINGS = (
    "Use this when",
    "Do not use this when",
    "Required inputs",
    "Procedure",
    "Decision points",
    "Required evidence",
    "Stop conditions",
    "Completion criteria",
)
STANDARD_HEADINGS = (
    "Rules",
    "Review triggers",
    "Required response",
    "Exceptions",
    "Evidence",
)
POLICY_HEADINGS = (
    "Applies when",
    "Required action",
    "Required evidence",
    "Exceptions",
)
ACCEPTANCE_HEADINGS = (
    "Required evidence",
    "Waiver conditions",
    "Failure conditions",
)
NUMBERED_STEP = re.compile(r"(?m)^1\.\s+\S")
SECTION = re.compile(r"(?ms)^## (?P<title>[^\n]+)\n(?P<body>.*?)(?=^## |\Z)")


def _document_errors(text: str) -> list[str]:
    try:
        document = parse_frontmatter(text)
    except ValueError as exc:
        return [str(exc)]
    errors: list[str] = []
    for key in ("id", "version", "status"):
        if not isinstance(document.data.get(key), str) or not document.data[key].strip():
            errors.append(f"missing front-matter field: {key}")
    if not any(line.startswith("# ") for line in document.body.splitlines()):
        errors.append("missing H1 heading")
    return errors


def _sections(text: str) -> dict[str, str]:
    return {
        match.group("title").strip(): match.group("body").strip()
        for match in SECTION.finditer(text)
    }


def _missing_headings(text: str, headings: tuple[str, ...]) -> list[str]:
    sections = _sections(text)
    errors: list[str] = []
    for heading in headings:
        if heading not in sections:
            errors.append(f"missing heading: {heading}")
        elif not sections[heading]:
            errors.append(f"empty section: {heading}")
    return errors


def validate_workflow_text(text: str) -> list[str]:
    errors = _document_errors(text) + _missing_headings(text, WORKFLOW_HEADINGS)
    if "## Procedure" in text and not NUMBERED_STEP.search(text):
        errors.append("Procedure must contain ordered executable steps")
    return errors


def validate_standard_text(text: str) -> list[str]:
    return _document_errors(text) + _missing_headings(text, STANDARD_HEADINGS)


def validate_policy_text(text: str) -> list[str]:
    errors = _document_errors(text) + _missing_headings(text, POLICY_HEADINGS)
    if "## Required action" in text and not NUMBERED_STEP.search(text):
        errors.append("Required action must contain ordered executable steps")
    return errors


def validate_acceptance_text(text: str) -> list[str]:
    errors = _document_errors(text) + _missing_headings(text, ACCEPTANCE_HEADINGS)
    if "## Pass conditions" not in text and "## Gate statuses" not in text:
        errors.append("missing heading: Pass conditions")
    return errors


def validate_skill_content(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    groups = (
        (root / "skill/workflows", validate_workflow_text),
        (root / "skill/standards", validate_standard_text),
        (root / "skill/acceptance", validate_acceptance_text),
        (root / "skill/policies", validate_policy_text),
    )
    for base, validator in groups:
        for path in sorted(base.rglob("*.md")):
            for message in validator(path.read_text(encoding="utf-8")):
                errors.append(f"{path.relative_to(root)}: {message}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate canonical skill-document contracts.")
    parser.add_argument("--repository-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args(argv)
    errors = validate_skill_content(args.repository_root)
    for error in errors:
        print(error)
    if errors:
        return 1
    print("skill-content validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
