#!/usr/bin/env python3
"""Configure GitHub environments, Pages, and the PyPI secret for GetDone.

This source-only helper requires an authenticated GitHub CLI session with
administration access to the target repository. It never stores the PyPI token
on disk; the token is read from standard input when requested.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


def _run(*args: str, input_text: str | None = None) -> CommandResult:
    completed = subprocess.run(
        list(args),
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)


def _require_gh() -> None:
    if shutil.which("gh") is None:
        raise RuntimeError("GitHub CLI 'gh' is not installed")
    status = _run("gh", "auth", "status")
    if status.returncode != 0:
        raise RuntimeError("GitHub CLI is not authenticated; run 'gh auth login'")


def _repository(explicit: str | None) -> str:
    if explicit:
        return explicit
    result = _run("gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner")
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError("Could not infer the GitHub repository; pass --repository OWNER/REPO")
    return result.stdout.strip()


def _ensure_environment(repository: str) -> None:
    result = _run(
        "gh", "api", "--method", "PUT",
        f"repos/{repository}/environments/pypi",
        "-H", "Accept: application/vnd.github+json",
    )
    if result.returncode != 0:
        raise RuntimeError(f"Could not create the pypi environment: {result.stderr.strip()}")


def _set_secret(repository: str) -> None:
    if sys.stdin.isatty():
        print("Paste the PyPI API token, then press Ctrl-D (Unix/macOS) or Ctrl-Z Enter (Windows):")
    token = sys.stdin.read().strip()
    if not token:
        raise RuntimeError("No PyPI token was supplied on standard input")
    result = _run(
        "gh", "secret", "set", "PYPI_API_TOKEN",
        "--env", "pypi", "--repo", repository,
        input_text=token,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Could not set PYPI_API_TOKEN: {result.stderr.strip()}")


def _enable_pages(repository: str) -> None:
    get_result = _run("gh", "api", f"repos/{repository}/pages")
    if get_result.returncode == 0:
        payload = json.loads(get_result.stdout)
        if payload.get("build_type") == "workflow":
            return
        result = _run(
            "gh", "api", "--method", "PUT", f"repos/{repository}/pages",
            "-f", "build_type=workflow",
        )
    else:
        result = _run(
            "gh", "api", "--method", "POST", f"repos/{repository}/pages",
            "-f", "build_type=workflow",
        )
    if result.returncode != 0:
        raise RuntimeError(f"Could not enable GitHub Pages workflow mode: {result.stderr.strip()}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Configure GetDone GitHub release settings.")
    parser.add_argument("--repository", help="GitHub repository in OWNER/REPO form")
    parser.add_argument(
        "--set-pypi-token", action="store_true",
        help="Read a PyPI API token from standard input and store it in the pypi environment",
    )
    parser.add_argument(
        "--skip-pages", action="store_true", help="Do not configure GitHub Pages workflow mode"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        _require_gh()
        repository = _repository(args.repository)
        _ensure_environment(repository)
        if args.set_pypi_token:
            _set_secret(repository)
        if not args.skip_pages:
            _enable_pages(repository)
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"GitHub release settings configured for {repository}")
    print("Manual hardening still recommended: protect main and v* tags; optionally require pypi approval.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
