#!/usr/bin/env python3
"""Validate repository structure, product boundaries, and skill contracts."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from getdone.adapters import validate_adapter_repository
    from development.tools.benchmark_context_selection import validate_published_report
    from getdone.catalogue import validate_catalogue_repository
    from getdone.catalogue_overlays import validate_overlay_file
    from development.tools.documentation_site import validate_documentation
    from getdone.project_records import validate_profile_record_templates
    from development.tools.public_contracts import validate_public_contracts
    from development.tools.registry_indexes import validate_registry_indexes
    from development.tools.rollout_validation import validate_committed_report
    from development.tools.validate_frontmatter import (
        validate_bootstrap_manifest,
        validate_bootstrap_template_files,
        validate_workflow_files,
    )
    from development.tools.validate_skill_content import validate_skill_content
except ModuleNotFoundError as exc:  # Direct execution from the tooling directory.
    direct_names = {
        "getdone",
        "getdone.adapters",
        "development.tools.benchmark_context_selection",
        "getdone.catalogue",
        "getdone.catalogue_overlays",
        "development.tools.documentation_site",
        "getdone.project_records",
        "development.tools.public_contracts",
        "development.tools.registry_indexes",
        "development.tools.rollout_validation",
        "development.tools.validate_frontmatter",
        "development.tools.validate_skill_content",
    }
    if exc.name not in direct_names:
        raise
    from adapters import validate_adapter_repository
    from benchmark_context_selection import validate_published_report
    from catalogue import validate_catalogue_repository
    from catalogue_overlays import validate_overlay_file
    from documentation_site import validate_documentation
    from project_records import validate_profile_record_templates
    from public_contracts import validate_public_contracts
    from registry_indexes import validate_registry_indexes
    from rollout_validation import validate_committed_report
    from validate_frontmatter import (
        validate_bootstrap_manifest,
        validate_bootstrap_template_files,
        validate_workflow_files,
    )
    from validate_skill_content import validate_skill_content

LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
WORKFLOW_ID_PATTERN = re.compile(r"^id:\s*(\S+)\s*$", re.MULTILINE)
ROUTER_PATH_PATTERN = re.compile(r"`(workflows/[^`]+\.md)`")


@dataclass(frozen=True)
class ValidationError:
    path: Path
    message: str


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


REQUIRED_PATHS = (
    Path("AGENTS.md"),
    Path("README.md"),
    Path("skill/README.md"),
    Path("skill/START-HERE.md"),
    Path("skill/workflow-router.md"),
    Path("skill/workflows/general/deterministic-development.md"),
    Path("skill/standards/core.md"),
    Path("skill/standards/languages/python.md"),
    Path("skill/standards/languages/typescript.md"),
    Path("skill/acceptance/core.md"),
    Path("skill/acceptance/change-types/feature.md"),
    Path("skill/policies/shared-repository-mutability.md"),
    Path("skill/bootstrap/templates/minimal"),
    Path("skill/bootstrap/templates/standard"),
    Path("skill/bootstrap/manifests.json"),
    Path("skill/adapters/manifest.json"),
    Path("skill/registry/reuse-catalogue.json"),
    Path("skill/registry/workflows.json"),
    Path("skill/contracts/public-contracts.json"),
    Path("skill/contracts/project-records.json"),
    Path("skill/contracts/project-records.md"),
    Path("skill/schemas/workflow-frontmatter.schema.json"),
    Path("skill/schemas/context-selection-manifest.schema.json"),
    Path("skill/schemas/project-record-contracts.schema.json"),
    Path("development/tools"),
    Path("development/scripts"),
    Path("development/benchmarks"),
    Path("development/benchmarks/context-selection/cases.json"),
    Path("development/rollout"),
    Path("development/rollout/cases.json"),
    Path("docs/quickstart.md"),
    Path("docs/rollout-readiness.md"),
    Path("zensical.toml"),
    Path("site_docs/index.md"),
    Path("site_docs/catalogue/index.md"),
)
FORBIDDEN_LEGACY_ROOTS = (
    Path("skills"),
    Path("best-practices"),
    Path("acceptance"),
    Path("policies"),
    Path("adapters"),
    Path("project-bootstrap"),
    Path("catalogue"),
    Path("registry"),
    Path("contracts"),
    Path("schemas"),
    Path("templates"),
    Path("devtools"),
    Path("scripts"),
    Path("benchmarks"),
    Path("rollout"),
)


def validate_required_paths(root: Path) -> list[ValidationError]:
    return [
        ValidationError(path, "required path does not exist")
        for path in REQUIRED_PATHS
        if not (root / path).exists()
    ]


def validate_product_boundary(root: Path) -> list[ValidationError]:
    errors = [
        ValidationError(path, "obsolete top-level directory must be moved to its canonical location")
        for path in FORBIDDEN_LEGACY_ROOTS
        if (root / path).exists()
    ]
    if not (root / "skill").is_dir():
        errors.append(ValidationError(Path("skill"), "skill product root is missing"))
    return errors


def validate_markdown_links(root: Path) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for path in root.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for target in LINK_PATTERN.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#", maxsplit=1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                errors.append(
                    ValidationError(path.relative_to(root), f"broken link target: {target}")
                )
    return errors



def validate_product_links_stay_inside_skill(root: Path) -> list[ValidationError]:
    errors: list[ValidationError] = []
    skill_root = (root / "skill").resolve()
    for path in skill_root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for target in LINK_PATTERN.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#", maxsplit=1)[0]
            if not clean:
                continue
            resolved = (path.parent / clean).resolve()
            if not resolved.is_relative_to(skill_root):
                errors.append(
                    ValidationError(
                        path.relative_to(root),
                        f"product link leaves skill boundary: {target}",
                    )
                )
    return errors

def validate_workflow_ids(root: Path) -> list[ValidationError]:
    errors: list[ValidationError] = []
    seen: dict[str, Path] = {}
    for path in (root / "skill/workflows").rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        match = WORKFLOW_ID_PATTERN.search(text)
        if not match:
            errors.append(ValidationError(path.relative_to(root), "missing front-matter id"))
            continue
        workflow_id = match.group(1)
        previous = seen.get(workflow_id)
        if previous:
            errors.append(
                ValidationError(
                    path.relative_to(root),
                    f"duplicate workflow id '{workflow_id}' also used by {previous}",
                )
            )
        seen[workflow_id] = path.relative_to(root)
    return errors


def validate_workflow_references(root: Path) -> list[ValidationError]:
    router = root / "skill/workflow-router.md"
    if not router.is_file():
        return [ValidationError(Path("skill/workflow-router.md"), "workflow router is missing")]
    errors: list[ValidationError] = []
    for relative in sorted(set(ROUTER_PATH_PATTERN.findall(router.read_text(encoding="utf-8")))):
        if not (root / "skill" / relative).is_file():
            errors.append(
                ValidationError(
                    Path("skill/workflow-router.md"),
                    f"referenced workflow does not exist: {relative}",
                )
            )
    return errors


def _messages(prefix: Path, values: list[str]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for value in values:
        path_text, separator, detail = value.partition(": ")
        errors.append(ValidationError(Path(path_text) if separator else prefix, detail or value))
    return errors


def validate_frontmatter_schemas(root: Path) -> list[ValidationError]:
    messages = validate_workflow_files(root)
    messages.extend(validate_bootstrap_template_files(root))
    messages.extend(validate_bootstrap_manifest(root))
    return _messages(Path("skill"), messages)


def validate_adapter_contracts(root: Path) -> list[ValidationError]:
    return _messages(Path("skill/adapters"), validate_adapter_repository(root))


def validate_catalogue_contracts(root: Path) -> list[ValidationError]:
    return _messages(Path("skill/registry"), validate_catalogue_repository(root))


def validate_documentation_contracts(root: Path) -> list[ValidationError]:
    return [
        ValidationError(Path(message.split(" is ", maxsplit=1)[0]), message)
        for message in validate_documentation(root)
    ]


def validate_registry_index_contracts(root: Path) -> list[ValidationError]:
    return [
        ValidationError(Path(message.split(" is ", maxsplit=1)[0]), message)
        for message in validate_registry_indexes(root)
    ]


def validate_example_overlay(root: Path) -> list[ValidationError]:
    overlay = (
        root
        / "skill/references/examples/organisation-catalogue-overlay/registry-overlay.json"
    )
    return [
        ValidationError(Path("skill/references/examples/organisation-catalogue-overlay"), message)
        for message in validate_overlay_file(overlay, schema_root=root)
    ]


def validate_context_selection_contracts(root: Path) -> list[ValidationError]:
    return [
        ValidationError(Path("development/benchmarks/context-selection"), message)
        for message in validate_published_report(root)
    ]


def validate_rollout_contracts(root: Path) -> list[ValidationError]:
    return [
        ValidationError(Path("development/rollout/results/1.0.0.json"), message)
        for message in validate_committed_report(root)
    ]


def validate_project_record_contracts(root: Path) -> list[ValidationError]:
    return _messages(
        Path("skill/bootstrap/templates"),
        validate_profile_record_templates(root),
    )


def validate_public_contract_freeze(root: Path) -> list[ValidationError]:
    return [
        ValidationError(Path("skill/contracts/public-contracts.json"), message)
        for message in validate_public_contracts(root)
    ]


def validate_no_live_project_state(root: Path) -> list[ValidationError]:
    forbidden = (
        root / ".agent/current",
        root / ".agent/journal",
        root / ".agent/tracking",
    )
    return [
        ValidationError(path.relative_to(root), "live project state is forbidden in shared repo")
        for path in forbidden
        if path.exists()
    ]


def validate_repository(root: Path) -> list[ValidationError]:
    root = root.resolve()
    errors: list[ValidationError] = []
    errors.extend(validate_required_paths(root))
    errors.extend(validate_product_boundary(root))
    errors.extend(validate_markdown_links(root))
    errors.extend(validate_product_links_stay_inside_skill(root))
    errors.extend(validate_workflow_ids(root))
    errors.extend(validate_workflow_references(root))
    errors.extend(validate_frontmatter_schemas(root))
    errors.extend(_messages(Path("skill"), validate_skill_content(root)))
    errors.extend(validate_adapter_contracts(root))
    errors.extend(validate_catalogue_contracts(root))
    errors.extend(validate_registry_index_contracts(root))
    errors.extend(validate_documentation_contracts(root))
    errors.extend(validate_example_overlay(root))
    errors.extend(validate_context_selection_contracts(root))
    errors.extend(validate_project_record_contracts(root))
    errors.extend(validate_public_contract_freeze(root))
    errors.extend(validate_rollout_contracts(root))
    errors.extend(validate_no_live_project_state(root))
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate the shared skills repository.")
    parser.add_argument("--repository-root", type=Path, default=repository_root())
    return parser


def main(argv: list[str] | None = None) -> int:
    root = build_parser().parse_args(argv).repository_root.resolve()
    errors = validate_repository(root)
    if errors:
        for error in errors:
            print(f"{error.path}: {error.message}", file=sys.stderr)
        print(f"validation failed: {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
