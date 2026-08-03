"""Observable tests for the golden-path greeting feature."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from greeting import greet


class GreetingTests(unittest.TestCase):
    def test_greets_trimmed_name(self) -> None:
        self.assertEqual("Hello, Ada!", greet("  Ada  "))

    def test_rejects_empty_name(self) -> None:
        with self.assertRaisesRegex(ValueError, "name must not be empty"):
            greet("   ")


if __name__ == "__main__":
    unittest.main()
