#!/usr/bin/env python3
"""Install a thin agent-specific adapter into a bootstrapped project."""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from getdone.adapters import AdapterSpec, load_adapter_contract
    from getdone.initialise_project import repository_root
except ModuleNotFoundError:  # Direct execution from the tooling directory.
    from adapters import AdapterSpec, load_adapter_contract
    from initialise_project import repository_root


@dataclass(frozen=True)
class AdapterInstallResult:
    adapter_id: str
    status: str
    path: Path | None
    message: str


def _require_bootstrapped_project(project_root: Path) -> None:
    required = (
        project_root / "AGENTS.md",
        project_root / ".agent" / "skills-reference.md",
    )
    missing = [path.relative_to(project_root) for path in required if not path.is_file()]
    if missing:
        paths = ", ".join(path.as_posix() for path in missing)
        raise ValueError(f"project is not bootstrapped; missing: {paths}")


def _reference_result(spec: AdapterSpec, project_root: Path) -> AdapterInstallResult:
    if spec.delivery == "bootstrap-managed":
        if spec.destination is None or not (project_root / spec.destination).is_file():
            raise ValueError(f"bootstrap-managed adapter '{spec.adapter_id}' is not present")
        return AdapterInstallResult(
            spec.adapter_id,
            "bootstrap-managed",
            spec.destination,
            "the bootstrap-managed project instructions already provide this adapter",
        )
    return AdapterInstallResult(
        spec.adapter_id,
        "reference-only",
        None,
        "this adapter is supplied through conversation or workspace context",
    )


def install_adapter(
    project_root: Path,
    adapter_id: str,
    *,
    skills_root: Path | None = None,
    overwrite: bool = False,
) -> AdapterInstallResult:
    project_root = project_root.resolve()
    skills_root = (skills_root or repository_root()).resolve()
    _require_bootstrapped_project(project_root)

    contract = load_adapter_contract(skills_root)
    spec = contract.adapters.get(adapter_id)
    if spec is None:
        valid = ", ".join(sorted(contract.adapters))
        raise ValueError(f"unknown adapter '{adapter_id}'. Valid adapters: {valid}")
    if spec.delivery != "project-file":
        return _reference_result(spec, project_root)
    if spec.template is None or spec.destination is None:
        raise ValueError(f"adapter '{adapter_id}' has an incomplete project-file mapping")

    source = skills_root / spec.template
    destination = project_root / spec.destination
    if destination.exists() and not overwrite:
        return AdapterInstallResult(
            adapter_id,
            "skipped",
            spec.destination,
            "project-owned adapter file already exists",
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return AdapterInstallResult(adapter_id, "created", spec.destination, "adapter installed")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install a thin project-local agent adapter.")
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--skills-root", type=Path)
    parser.add_argument("--adapter")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--list", action="store_true", dest="list_adapters")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    skills_root = (args.skills_root or repository_root()).resolve()
    try:
        contract = load_adapter_contract(skills_root)
        if args.list_adapters:
            for spec in contract.adapters.values():
                print(f"{spec.adapter_id:16} {spec.delivery:18} {spec.display_name}")
            return 0
        if args.project_root is None or args.adapter is None:
            print(
                "error: --project-root and --adapter are required for installation",
                file=sys.stderr,
            )
            return 2
        result = install_adapter(
            args.project_root,
            args.adapter,
            skills_root=skills_root,
            overwrite=args.overwrite,
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    path = "-" if result.path is None else result.path.as_posix()
    print(f"{result.status}: {result.adapter_id} ({path}) - {result.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
