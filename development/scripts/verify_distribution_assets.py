#!/usr/bin/env python3
"""Verify that built Python distributions contain the immutable GetDone runtime assets."""

from __future__ import annotations

import argparse
import sys
import tarfile
import zipfile
from pathlib import Path


def _one(paths: list[Path], label: str) -> Path:
    if len(paths) != 1:
        raise ValueError(f"expected exactly one {label}, found {len(paths)}")
    return paths[0]


def _source_runtime_files(root: Path) -> tuple[str, ...]:
    skill_root = root / "skill"
    files = tuple(
        path.relative_to(root).as_posix()
        for path in sorted(skill_root.rglob("*"))
        if path.is_file()
    )
    if not files:
        raise ValueError("source skill tree is empty")
    return files


def _verify_wheel(wheel: Path, source_files: tuple[str, ...]) -> list[str]:
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
    expected = {"getdone/assets/VERSION"}
    expected.update(f"getdone/assets/{path}" for path in source_files)
    return sorted(expected - names)


def _verify_sdist(sdist: Path, source_files: tuple[str, ...]) -> list[str]:
    with tarfile.open(sdist, "r:gz") as archive:
        names = set()
        for member in archive.getmembers():
            parts = Path(member.name).parts
            if len(parts) > 1:
                names.add(Path(*parts[1:]).as_posix())
    expected = {"VERSION", *source_files}
    return sorted(expected - names)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--dist-dir", type=Path, default=Path("dist"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.repository_root.resolve()
    dist_dir = args.dist_dir.resolve()
    try:
        wheel = _one(sorted(dist_dir.glob("*.whl")), "wheel")
        sdist = _one(sorted(dist_dir.glob("*.tar.gz")), "sdist")
        source_files = _source_runtime_files(root)
        wheel_missing = _verify_wheel(wheel, source_files)
        sdist_missing = _verify_sdist(sdist, source_files)
    except (OSError, ValueError, tarfile.TarError, zipfile.BadZipFile) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for path in wheel_missing:
        print(f"error: wheel missing {path}", file=sys.stderr)
    for path in sdist_missing:
        print(f"error: sdist missing {path}", file=sys.stderr)
    if wheel_missing or sdist_missing:
        return 1

    print(
        f"distribution assets valid: {len(source_files)} skill file(s) "
        "present in wheel and sdist"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
