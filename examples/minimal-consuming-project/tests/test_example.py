from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from example_project import greeting


def test_greeting() -> None:
    assert greeting("Agent") == "Hello, Agent!"
