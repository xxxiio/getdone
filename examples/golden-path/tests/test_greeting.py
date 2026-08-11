"""Observable tests for the golden-path greeting feature."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from greeting import greet


def test_greets_trimmed_name() -> None:
    assert greet("  Ada  ") == "Hello, Ada!"


def test_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="name must not be empty"):
        greet("   ")
