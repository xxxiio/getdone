from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from slug_policy import render_slug


def test_normalises_whitespace_and_punctuation() -> None:
    assert render_slug(" Agent Development: Skills ") == "agent-development-skills"


def test_supports_an_explicit_separator() -> None:
    assert render_slug("Agent Development Skills", separator="_") == "agent_development_skills"


def test_rejects_an_empty_separator() -> None:
    with pytest.raises(ValueError):
        render_slug("Agent Skills", separator="")
