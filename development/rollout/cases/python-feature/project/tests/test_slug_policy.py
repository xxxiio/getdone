from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from slug_policy import render_slug


class SlugPolicyTests(unittest.TestCase):
    def test_normalises_whitespace_and_punctuation(self) -> None:
        self.assertEqual("agent-development-skills", render_slug(" Agent Development: Skills "))

    def test_supports_an_explicit_separator(self) -> None:
        self.assertEqual(
            "agent_development_skills",
            render_slug("Agent Development Skills", separator="_"),
        )

    def test_rejects_an_empty_separator(self) -> None:
        with self.assertRaises(ValueError):
            render_slug("Agent Skills", separator="")


if __name__ == "__main__":
    unittest.main()
