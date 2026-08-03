#!/usr/bin/env python3
"""Build the read-only skill product archive without repository-development files."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


def build_skill_pack(root: Path, output: Path) -> Path:
    root = root.resolve()
    skill_root = root / "skill"
    if not skill_root.is_dir():
        raise FileNotFoundError(f"skill product directory does not exist: {skill_root}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(root / "VERSION", "VERSION")
        for path in sorted(item for item in skill_root.rglob("*") if item.is_file()):
            archive.write(path, path.relative_to(root).as_posix())
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the standalone agent skill pack.")
    parser.add_argument("--repository-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    print(build_skill_pack(args.repository_root, args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
