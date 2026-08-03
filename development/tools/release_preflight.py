#!/usr/bin/env python3
"""Run the complete local GetDone release preflight."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from development.tools.build_skill_pack import build_skill_pack


@dataclass(frozen=True)
class Step:
    name: str
    command: tuple[str, ...]
    required_executable: str | None = None


def _run(root: Path, step: Step) -> bool:
    if step.required_executable and shutil.which(step.required_executable) is None:
        print(f"FAIL {step.name}: {step.required_executable} is not installed", file=sys.stderr)
        return False
    print(f"==> {step.name}")
    completed = subprocess.run(step.command, cwd=root, check=False)
    if completed.returncode:
        print(f"FAIL {step.name} (exit {completed.returncode})", file=sys.stderr)
        return False
    print(f"PASS {step.name}")
    return True


def _write_checksums(dist: Path, version: str) -> Path:
    """Write deterministic SHA-256 checksums for release artifacts."""

    checksum_path = dist / f"getdone-{version}-SHA256SUMS.txt"
    artifacts = sorted(path for path in dist.iterdir() if path.is_file() and path != checksum_path)
    lines = []
    for artifact in artifacts:
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        lines.append(f"{digest}  {artifact.name}")
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return checksum_path


def run_preflight(root: Path, *, skip_site: bool = False) -> int:
    """Validate, build, inspect, and smoke-test release distributions."""

    root = root.resolve()
    python = sys.executable
    dist = root / "dist"
    if dist.exists():
        shutil.rmtree(dist)

    steps = [
        Step("release metadata", (python, "development/scripts/verify_release.py", "--repository-root", ".")),
        Step("registry indexes", (python, "-m", "development.tools.generate_registry_indexes", "--repository-root", ".")),
        Step("generated documentation", (python, "development/scripts/generate_docs.py", "--repository-root", ".")),
        Step("repository validation", (python, "development/scripts/validate_repository.py", "--repository-root", ".")),
        Step("unit tests", (python, "-m", "unittest", "discover", "-s", "tests")),
    ]
    if not skip_site:
        steps.append(Step("strict documentation site", ("zensical", "build", "--strict"), "zensical"))
    for step in steps:
        if not _run(root, step):
            return 1

    build_available = subprocess.run(
        [python, "-c", "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('build.__main__') else 1)"], capture_output=True, check=False
    ).returncode == 0
    if build_available:
        if not _run(root, Step("build distributions", (python, "-m", "build"))):
            return 1
    else:
        print("WARN build package is unavailable; building the wheel with pip instead")
        if not _run(
            root,
            Step(
                "build wheel fallback",
                (python, "-m", "pip", "wheel", ".", "--no-deps", "-w", "dist"),
            ),
        ):
            return 1

    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    skill_pack = dist / f"getdone-skill-pack-{version}.zip"
    build_skill_pack(root, skill_pack)
    if not skill_pack.is_file():
        print("FAIL skill-pack build: archive was not created", file=sys.stderr)
        return 1

    files = sorted((*dist.glob("*.whl"), *dist.glob("*.tar.gz")))
    if not files:
        print("FAIL distribution check: dist/ is empty", file=sys.stderr)
        return 1
    twine_available = subprocess.run(
        [python, "-c", "import twine"], capture_output=True, check=False
    ).returncode == 0
    if twine_available:
        completed = subprocess.run(
            [python, "-m", "twine", "check", *map(str, files)], cwd=root, check=False
        )
        if completed.returncode:
            return completed.returncode
        print("PASS Twine distribution check")
    else:
        import zipfile

        wheels_for_metadata = sorted(dist.glob("*.whl"))
        if len(wheels_for_metadata) != 1:
            print("FAIL metadata fallback: expected exactly one wheel", file=sys.stderr)
            return 1
        with zipfile.ZipFile(wheels_for_metadata[0]) as archive:
            metadata = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
            if len(metadata) != 1:
                print("FAIL metadata fallback: wheel METADATA is missing or ambiguous", file=sys.stderr)
                return 1
            text = archive.read(metadata[0]).decode("utf-8")
            if "Name: getdone-dev" not in text or f"Version: {version}" not in text:
                print("FAIL metadata fallback: unexpected distribution name or version", file=sys.stderr)
                return 1
        print("WARN Twine is unavailable; direct wheel metadata inspection passed")

    wheels = sorted(dist.glob("*.whl"))
    if len(wheels) != 1:
        print(f"FAIL wheel smoke test: expected one wheel, found {len(wheels)}", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory(prefix="getdone-release-") as directory:
        target = Path(directory) / "site"
        target.mkdir()
        install = subprocess.run(
            [python, "-m", "pip", "install", "--no-deps", "--target", str(target), str(wheels[0])],
            cwd=directory,
            check=False,
        )
        if install.returncode:
            print("FAIL installed-wheel smoke test: wheel installation failed", file=sys.stderr)
            return 1
        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(target)
        for arguments in (["-m", "getdone.cli", "--version"], ["-m", "getdone.cli", "--help"]):
            command = [python, *arguments]
            if subprocess.run(command, cwd=directory, env=environment, check=False).returncode:
                print(f"FAIL installed-wheel smoke test: {' '.join(command)}", file=sys.stderr)
                return 1
    print("PASS installed-wheel smoke test")
    checksum_path = _write_checksums(dist, version)
    print(f"PASS release checksums: {checksum_path.name}")
    print("Release preflight passed. The remaining steps require GitHub/PyPI account access.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--skip-site",
        action="store_true",
        help="Skip the local Zensical render; hosted CI must still run it.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run_preflight(args.repository_root, skip_site=args.skip_site)


if __name__ == "__main__":
    raise SystemExit(main())
