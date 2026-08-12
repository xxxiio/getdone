"""Setuptools build hooks for bundling immutable GetDone runtime assets."""

from __future__ import annotations

import shutil
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py

ROOT = Path(__file__).resolve().parent
PACKAGE_ASSET_ROOT = Path("getdone") / "assets"


def _runtime_assets() -> tuple[tuple[Path, Path], ...]:
    assets: list[tuple[Path, Path]] = [(ROOT / "VERSION", Path("VERSION"))]
    skill_root = ROOT / "skill"
    assets.extend(
        (source, Path("skill") / source.relative_to(skill_root))
        for source in sorted(skill_root.rglob("*"))
        if source.is_file()
    )
    return tuple(assets)


class build_py(_build_py):
    """Copy immutable runtime assets into the installed getdone package."""

    def run(self) -> None:
        super().run()
        destination_root = Path(self.build_lib) / PACKAGE_ASSET_ROOT
        for source, relative in _runtime_assets():
            destination = destination_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    def get_outputs(self, include_bytecode: bool = True) -> list[str]:
        outputs = list(super().get_outputs(include_bytecode=include_bytecode))
        destination_root = Path(self.build_lib) / PACKAGE_ASSET_ROOT
        outputs.extend(str(destination_root / relative) for _, relative in _runtime_assets())
        return outputs


setup(cmdclass={"build_py": build_py})
