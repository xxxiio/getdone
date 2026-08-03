#!/usr/bin/env python3
"""Verify repository release metadata and optional Git tag properties."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReleaseVerificationReport:
    version: str | None
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return not self.errors


def _read_version(root: Path) -> tuple[str | None, list[str]]:
    path = root / "VERSION"
    if not path.is_file():
        return None, ["VERSION file is missing"]
    version = path.read_text(encoding="utf-8").strip()
    if not version:
        return None, ["VERSION file is empty"]
    return version, []


def _version_source_errors(root: Path) -> list[str]:
    """Ensure packaging derives its version from the standalone skill-pack version."""

    path = root / "pyproject.toml"
    if not path.is_file():
        return ["pyproject.toml is missing"]
    payload = tomllib.loads(path.read_text(encoding="utf-8"))
    project = payload.get("project")
    if not isinstance(project, dict):
        return ["pyproject.toml has no [project] table"]
    errors: list[str] = []
    if "version" in project:
        errors.append("pyproject.toml must not contain a duplicate literal project.version")
    dynamic = project.get("dynamic")
    if not isinstance(dynamic, list) or "version" not in dynamic:
        errors.append("pyproject.toml must declare version as dynamic")
    setuptools = payload.get("tool", {}).get("setuptools", {})
    version_config = setuptools.get("dynamic", {}).get("version") if isinstance(setuptools, dict) else None
    if not isinstance(version_config, dict) or version_config.get("file") != ["VERSION"]:
        errors.append("pyproject.toml must derive its dynamic version from VERSION")
    return errors


def _metadata_errors(root: Path, version: str) -> list[str]:
    errors: list[str] = []
    errors.extend(_version_source_errors(root))
    changelog = root / "CHANGELOG.md"
    if not changelog.is_file():
        errors.append("CHANGELOG.md is missing")
    elif f"## {version} - " not in changelog.read_text(encoding="utf-8"):
        errors.append(f"changelog has no release heading for {version}")
    return errors


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )


def _tag_findings(
    root: Path,
    tag: str,
    *,
    require_signature: bool,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    kind = _git(root, "cat-file", "-t", tag)
    if kind.returncode != 0:
        return [f"tag '{tag}' does not exist"], warnings
    if kind.stdout.strip() != "tag":
        errors.append(f"tag '{tag}' is lightweight; an annotated tag is required")
        return errors, warnings

    verification = _git(root, "verify-tag", tag)
    if verification.returncode == 0:
        return errors, warnings
    detail = (verification.stderr or verification.stdout).strip()
    if require_signature:
        errors.append(f"tag '{tag}' signature verification failed: {detail}")
    else:
        warnings.append(f"tag '{tag}' is annotated but not signature-verified: {detail}")
    return errors, warnings


def verify_release_metadata(
    root: Path,
    *,
    tag: str | None = None,
    require_signature: bool = False,
) -> ReleaseVerificationReport:
    root = root.resolve()
    version, errors = _read_version(root)
    warnings: list[str] = []
    if version is not None:
        errors.extend(_metadata_errors(root, version))
        if tag is not None and tag != f"v{version}":
            errors.append(f"tag '{tag}' does not match release version 'v{version}'")
    if tag is not None:
        tag_errors, tag_warnings = _tag_findings(
            root,
            tag,
            require_signature=require_signature,
        )
        errors.extend(tag_errors)
        warnings.extend(tag_warnings)
    return ReleaseVerificationReport(version, tuple(errors), tuple(warnings))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify release metadata and tag integrity.")
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--tag")
    parser.add_argument("--require-signature", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = verify_release_metadata(
        args.repository_root,
        tag=args.tag,
        require_signature=args.require_signature,
    )
    for warning in report.warnings:
        print(f"warning: {warning}")
    for error in report.errors:
        print(f"error: {error}", file=sys.stderr)
    if not report.is_valid:
        return 1
    print(f"release metadata valid for {report.version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
