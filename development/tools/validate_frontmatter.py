#!/usr/bin/env python3
"""Validate Markdown YAML front matter against repository JSON schemas."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

try:
    from getdone.frontmatter import parse_frontmatter
    from getdone.profiles import collect_profile_templates, load_profiles, resolve_profile
except ModuleNotFoundError:  # Direct execution from the tooling directory.
    from frontmatter import parse_frontmatter
    from profiles import collect_profile_templates, load_profiles, resolve_profile


def validate_document_against_schema(text: str, schema: dict[str, Any]) -> list[str]:
    try:
        document = parse_frontmatter(text)
    except (ValueError, yaml.YAMLError) as exc:
        return [str(exc)]

    if not document.has_frontmatter:
        return ["document has no YAML front matter"]

    validator = Draft202012Validator(schema)
    messages: list[str] = []
    for error in sorted(validator.iter_errors(document.data), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "frontmatter"
        messages.append(f"{location}: {error.message}")
    return messages


def validate_workflow_files(root: Path) -> list[str]:
    schema_path = root / "skill/schemas/workflow-frontmatter.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    workflows_root = root / "skill/workflows"
    for path in sorted(workflows_root.rglob("*.md")):
        for message in validate_document_against_schema(
            path.read_text(encoding="utf-8"), schema
        ):
            errors.append(f"{path.relative_to(root)}: {message}")
    return errors


def validate_bootstrap_template_files(root: Path) -> list[str]:
    schema_path = root / "skill/schemas/bootstrap-template-frontmatter.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    templates_root = root / "skill/bootstrap/templates"
    for path in sorted(templates_root.rglob("*.md")):
        for message in validate_document_against_schema(
            path.read_text(encoding="utf-8"), schema
        ):
            errors.append(f"{path.relative_to(root)}: {message}")
    return errors


def validate_bootstrap_manifest(root: Path) -> list[str]:
    schema = json.loads(
        (root / "skill/schemas/bootstrap-manifest.schema.json").read_text(encoding="utf-8")
    )
    manifest_path = root / "skill/bootstrap/manifests.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors: list[str] = []
    for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "manifest"
        errors.append(f"{manifest_path.relative_to(root)}: {location}: {error.message}")
    if errors:
        return errors

    try:
        profiles = load_profiles(root)
        for profile_name in sorted(profiles):
            resolved = resolve_profile(profiles, profile_name)
            collect_profile_templates(root, resolved, profiles=profiles)
    except (OSError, ValueError) as exc:
        errors.append(f"{manifest_path.relative_to(root)}: {exc}")
    return errors


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate shared-repository Markdown front matter and profile manifests."
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=repository_root(),
        help="Path to the shared skills repository.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    root = build_parser().parse_args(argv).repository_root.resolve()
    errors = validate_workflow_files(root)
    errors.extend(validate_bootstrap_template_files(root))
    errors.extend(validate_bootstrap_manifest(root))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"front-matter validation failed: {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("front-matter validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
