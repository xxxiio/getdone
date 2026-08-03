from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from example_project import greeting


class GreetingTests(unittest.TestCase):
    def test_greeting(self) -> None:
        self.assertEqual("Hello, Agent!", greeting("Agent"))


if __name__ == "__main__":
    unittest.main()
