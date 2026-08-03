#!/usr/bin/env python3
"""Check or regenerate human-readable indexes from machine-readable registries."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from development.tools.registry_indexes import validate_registry_indexes, write_registry_indexes
except ModuleNotFoundError as exc:  # Direct execution from the tooling directory.
    if exc.name not in {"getdone", "development.tools.registry_indexes"}:
        raise
    from registry_indexes import validate_registry_indexes, write_registry_indexes


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check or generate registry Markdown indexes.")
    parser.add_argument("--repository-root", type=Path, default=repository_root())
    parser.add_argument("--write", action="store_true", help="Write generated indexes.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.repository_root.resolve()
    if args.write:
        for path in write_registry_indexes(root):
            print(f"wrote {path}")
        return 0
    errors = validate_registry_indexes(root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("registry indexes are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
