from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path

from development.tools.rollout_validation import REPORT_PATH, build_report, validate_report

ROOT = Path(__file__).resolve().parents[1]


class RolloutValidationTests(unittest.TestCase):
    def test_committed_report_matches_schema(self) -> None:
        report = json.loads((ROOT / REPORT_PATH).read_text(encoding="utf-8"))
        self.assertEqual([], validate_report(ROOT, report))
        self.assertTrue(report["summary"]["all_passed"])

    @unittest.skipUnless(shutil.which("g++"), "g++ is required for the C++ rollout case")
    def test_rollout_matrix_matches_committed_report(self) -> None:
        expected = json.loads((ROOT / REPORT_PATH).read_text(encoding="utf-8"))
        self.assertEqual(expected, build_report(ROOT))


if __name__ == "__main__":
    unittest.main()
