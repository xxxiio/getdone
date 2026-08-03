#!/usr/bin/env python3
"""Execute the bounded v1 rollout dogfood matrix."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

try:
    from getdone.context_selection import select_context
    from getdone.initialise_project import initialise_project
    from getdone.install_adapter import install_adapter
    from getdone.validate_project import validate_project
except ModuleNotFoundError as exc:  # Direct execution from the tooling directory.
    if exc.name not in {
        "getdone",
        "getdone.context_selection",
        "getdone.initialise_project",
        "getdone.install_adapter",
        "getdone.validate_project",
    }:
        raise
    from context_selection import select_context
    from initialise_project import initialise_project
    from install_adapter import install_adapter
    from validate_project import validate_project

REPORT_PATH = Path("development/rollout/results/1.0.0.json")


@dataclass(frozen=True)
class RolloutCase:
    case_id: str
    task_class: str
    language: str
    adapter: str
    project: Path
    task: Path
    solution: Path
    command: tuple[str, ...]
    before_expected: str


def _load_cases(root: Path) -> tuple[str, tuple[RolloutCase, ...]]:
    payload = json.loads((root / "development/rollout/cases.json").read_text(encoding="utf-8"))
    cases = tuple(
        RolloutCase(
            case_id=item["id"],
            task_class=item["task_class"],
            language=item["language"],
            adapter=item["adapter"],
            project=root / item["project"],
            task=root / item["task"],
            solution=root / item["solution"],
            command=tuple(item["test_command"]),
            before_expected=item["before_expected"],
        )
        for item in payload["cases"]
    )
    return payload["release_target"], cases


def _command(parts: tuple[str, ...]) -> list[str]:
    return [sys.executable if part == "{python}" else part for part in parts]


def _run_tests(project: Path, command: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        _command(command),
        cwd=project,
        check=False,
        capture_output=True,
        text=True,
    )


def _apply_solution(project: Path, solution: Path) -> None:
    for source in sorted(solution.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(solution)
        destination = project / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def _before_status(case: RolloutCase, result: subprocess.CompletedProcess[str]) -> str:
    passed = result.returncode == 0
    if case.before_expected == "fail" and passed:
        raise RuntimeError(f"{case.case_id}: baseline unexpectedly passed")
    if case.before_expected == "pass" and not passed:
        raise RuntimeError(f"{case.case_id}: baseline failed\n{result.stdout}{result.stderr}")
    return "passed" if passed else "expected-failure"


def _run_case(root: Path, case: RolloutCase, workspace: Path) -> dict[str, Any]:
    project = workspace / case.case_id
    shutil.copytree(case.project, project)
    before = _before_status(case, _run_tests(project, case.command))
    initialise_project(project, "standard", skills_root=root, skills_reference=".getdone")
    adapter = install_adapter(project, case.adapter, skills_root=root)
    selection = select_context(root, case.task_class, case.language)
    _apply_solution(project, case.solution)
    after = _run_tests(project, case.command)
    if after.returncode != 0:
        raise RuntimeError(f"{case.case_id}: completed tests failed\n{after.stdout}{after.stderr}")
    validation = validate_project(project, skills_root=root)
    if not validation.is_valid:
        details = "; ".join(f"{item.path}: {item.message}" for item in validation.errors)
        raise RuntimeError(f"{case.case_id}: project validation failed: {details}")
    return {
        "id": case.case_id,
        "task_class": case.task_class,
        "language": case.language,
        "adapter": case.adapter,
        "before": before,
        "after": "passed",
        "adapter_status": adapter.status,
        "project_validation": "passed",
        "context_documents": len(selection.documents),
        "context_tokens": selection.approximate_tokens,
    }


def build_report(root: Path) -> dict[str, Any]:
    release_target, cases = _load_cases(root)
    with tempfile.TemporaryDirectory() as directory:
        results = [_run_case(root, case, Path(directory)) for case in cases]
    return {
        "schema_version": 1,
        "release_target": release_target,
        "summary": {
            "case_count": len(results),
            "task_classes": sorted({item["task_class"] for item in results}),
            "languages": sorted({item["language"] for item in results}),
            "adapters": sorted({item["adapter"] for item in results}),
            "all_passed": True,
        },
        "cases": results,
        "limitations": [
            "Adapter delivery paths were exercised locally; independent vendor-agent "
            "runs remain external validation.",
            "The matrix validates small deterministic tasks and does not claim coverage "
            "of every project architecture.",
        ],
    }


def validate_report(root: Path, report: dict[str, Any]) -> list[str]:
    schema_path = root / "skill/schemas/rollout-report.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    return [error.message for error in sorted(validator.iter_errors(report), key=str)]


def validate_committed_report(root: Path) -> list[str]:
    root = root.resolve()
    try:
        report = json.loads((root / REPORT_PATH).read_text(encoding="utf-8"))
        release_target, cases = _load_cases(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [str(exc)]
    errors = validate_report(root, report)
    if report.get("release_target") != release_target:
        errors.append("rollout report release target differs from the case manifest")
    expected_ids = [case.case_id for case in cases]
    actual_ids = [item.get("id") for item in report.get("cases", [])]
    if actual_ids != expected_ids:
        errors.append("rollout report case order or identifiers differ from the case manifest")
    for case in cases:
        if not case.project.is_dir():
            errors.append(f"{case.case_id}: project fixture is missing")
        if not case.task.is_file():
            errors.append(f"{case.case_id}: task specification is missing")
        if not case.solution.is_dir():
            errors.append(f"{case.case_id}: solution directory is missing")
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the v1 rollout dogfood matrix.")
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument("--write", action="store_true", help="Write the committed rollout report.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when the committed report differs.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.repository_root.resolve()
    try:
        report = build_report(root)
        errors = validate_report(root, report)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    destination = root / REPORT_PATH
    if args.check:
        if not destination.is_file() or destination.read_text(encoding="utf-8") != rendered:
            print(f"error: rollout report drift: {REPORT_PATH}", file=sys.stderr)
            return 1
    if args.write:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    print(
        f"rollout passed: {report['summary']['case_count']} cases, "
        f"{len(report['summary']['languages'])} languages, "
        f"{len(report['summary']['adapters'])} adapters"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
