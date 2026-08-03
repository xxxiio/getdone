"""GetDone bootstrap, validation, and workflow tooling."""

from __future__ import annotations

import importlib.metadata

try:
    __version__ = importlib.metadata.version("get-done")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0+unknown"

__all__ = ["__version__"]
