#!/usr/bin/env python3
"""Check or generate the Zensical documentation catalogue."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from development.tools.documentation_site import validate_documentation, write_documentation
except ModuleNotFoundError as exc:
    if exc.name not in {"getdone", "development.tools.documentation_site"}:
        raise
    from documentation_site import validate_documentation, write_documentation


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check or generate Zensical catalogue pages.")
    parser.add_argument("--repository-root", type=Path, default=repository_root())
    parser.add_argument("--write", action="store_true", help="Write generated documentation pages.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.repository_root.resolve()
    if args.write:
        for path in write_documentation(root):
            print(f"wrote {path}")
        return 0
    errors = validate_documentation(root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("generated documentation is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
