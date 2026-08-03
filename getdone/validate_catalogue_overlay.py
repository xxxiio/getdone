#!/usr/bin/env python3
"""Validate an organisation catalogue overlay against a shared repository."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from getdone.catalogue_overlays import validate_overlay_file
except ModuleNotFoundError as exc:  # Direct execution from the tooling directory.
    if exc.name not in {"getdone", "getdone.catalogue_overlays"}:
        raise
    from catalogue_overlays import validate_overlay_file


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate one organisation catalogue overlay.")
    parser.add_argument("--repository-root", type=Path, default=repository_root())
    parser.add_argument("--overlay", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    errors = validate_overlay_file(
        args.overlay.resolve(),
        schema_root=args.repository_root.resolve(),
    )
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("overlay validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
