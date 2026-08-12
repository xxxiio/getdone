#!/usr/bin/env python3
"""Benchmark recurring context selection against representative static tasks."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

try:
    from getdone.context_selection import TASK_GATES, select_context
except ModuleNotFoundError as exc:  # Direct execution from the tooling directory.
    if exc.name not in {"getdone", "getdone.context_selection"}:
        raise
    from context_selection import TASK_GATES, select_context

COMMON_REQUIRED = (
    "skill/workflows/general/deterministic-development.md",
    "skill/standards/core.md",
    "skill/acceptance/core.md",
)
PUBLISHED_REPORT = Path("development/benchmarks/context-selection/results/1.1.0.json")
RC1_AVERAGE_SELECTED_TOKENS = 4856


def _baseline_documents(root: Path) -> tuple[str, ...]:
    return tuple(
        path.relative_to(root).as_posix()
        for path in sorted((root / "skill").rglob("*.md"))
    )


def _tokens(root: Path, paths: tuple[str, ...]) -> int:
    characters = sum(len((root / path).read_text(encoding="utf-8")) for path in paths)
    return max(1, math.ceil(characters / 4))


def _required_documents(case: dict[str, Any]) -> set[str]:
    required = set(COMMON_REQUIRED)
    required.update(case["required_documents"])
    if gate := TASK_GATES.get(case["task_class"]):
        required.add(gate)
    return required


def _case_result(root: Path, case: dict[str, Any], baseline_tokens: int) -> dict[str, Any]:
    selection = select_context(root, case["task_class"], case["language"])
    required = _required_documents(case)
    missing = sorted(required.difference(selection.documents))
    missed_gates = [path for path in missing if path.startswith("skill/acceptance/")]
    reduction = 1 - (selection.approximate_tokens / baseline_tokens)
    return {
        "id": case["id"],
        "route_correct": selection.workflow == case["expected_workflow"],
        "required_documents": len(required),
        "missing_documents": missing,
        "missed_acceptance_gates": missed_gates,
        "selected_documents": len(selection.documents),
        "selected_tokens": selection.approximate_tokens,
        "token_reduction": round(reduction, 4),
        "product_only": all(path.startswith("skill/") for path in selection.documents),
    }


def run_benchmark(root: Path) -> dict[str, Any]:
    root = root.resolve()
    fixture = json.loads((root / "development/benchmarks/context-selection/cases.json").read_text())
    baseline = _baseline_documents(root)
    baseline_tokens = _tokens(root, baseline)
    results = [_case_result(root, case, baseline_tokens) for case in fixture["cases"]]
    total_required = sum(item["required_documents"] for item in results)
    total_missing = sum(len(item["missing_documents"]) for item in results)
    reductions = [item["token_reduction"] for item in results]
    selected_tokens = [item["selected_tokens"] for item in results]
    route_accuracy = sum(item["route_correct"] for item in results) / len(results)
    recall = 1 - (total_missing / total_required)
    missed_gates = sum(len(item["missed_acceptance_gates"]) for item in results)
    average_selected = sum(selected_tokens) / len(selected_tokens)
    rc1_reduction = 1 - (average_selected / RC1_AVERAGE_SELECTED_TOKENS)
    justified = (
        route_accuracy == 1
        and recall == 1
        and missed_gates == 0
        and all(item["product_only"] for item in results)
        and max(item["selected_documents"] for item in results) <= 8
        and rc1_reduction >= 0.20
    )
    return {
        "schema_version": 2,
        "benchmark_cases": len(results),
        "baseline_documents": len(baseline),
        "baseline_tokens": baseline_tokens,
        "route_accuracy": round(route_accuracy, 4),
        "required_document_recall": round(recall, 4),
        "missed_acceptance_gates": missed_gates,
        "average_selected_tokens": round(average_selected),
        "average_token_reduction": round(sum(reductions) / len(reductions), 4),
        "minimum_token_reduction": min(reductions),
        "reduction_vs_rc1_selected_context": round(rc1_reduction, 4),
        "maximum_selected_documents": max(item["selected_documents"] for item in results),
        "tooling_justified": justified,
        "scope_note": "Static routing and document coverage; coding outcomes require dogfooding.",
        "cases": results,
    }


def validate_published_report(root: Path) -> list[str]:
    expected = run_benchmark(root)
    path = root / PUBLISHED_REPORT
    try:
        published = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path.relative_to(root)}: {exc}"]
    if published != expected:
        return [f"{path.relative_to(root)}: published benchmark report is stale"]
    if not expected["tooling_justified"]:
        return [f"{path.relative_to(root)}: context selector does not meet evidence gate"]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark deterministic context selection.")
    parser.add_argument("--repository-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = run_benchmark(args.repository_root)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"cases: {report['benchmark_cases']}")
        print(f"route accuracy: {report['route_accuracy']:.0%}")
        print(f"required document recall: {report['required_document_recall']:.0%}")
        print(f"reduction versus RC1 selection: {report['reduction_vs_rc1_selected_context']:.1%}")
        print(f"tooling justified: {str(report['tooling_justified']).lower()}")
    return 0 if report["tooling_justified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
