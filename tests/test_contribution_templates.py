from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class ContributionTemplateTests(unittest.TestCase):
    def test_issue_forms_are_valid_and_structured(self) -> None:
        expected = {
            "bug_report.yml",
            "feature_request.yml",
            "documentation.yml",
            "workflow_proposal.yml",
            "config.yml",
        }
        issue_dir = ROOT / ".github" / "ISSUE_TEMPLATE"
        self.assertEqual(expected, {path.name for path in issue_dir.glob("*.yml")})

        for path in issue_dir.glob("*.yml"):
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
            self.assertIsInstance(payload, dict)
            if path.name == "config.yml":
                self.assertFalse(payload["blank_issues_enabled"])
                continue
            self.assertIn("name", payload)
            self.assertIn("description", payload)
            self.assertIn("body", payload)
            self.assertGreaterEqual(len(payload["body"]), 4)

    def test_pull_request_template_requires_evidence_and_compatibility(self) -> None:
        text = (ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
        for phrase in (
            "Change impact",
            "Contract and compatibility",
            "Validation evidence",
            "Documentation and migration",
            "Next deterministic step",
        ):
            self.assertIn(phrase, text)

    def test_package_naming_contract_is_documented(self) -> None:
        text = (ROOT / "docs" / "package-naming.md").read_text(encoding="utf-8")
        self.assertIn("getdone-dev", text)
        self.assertIn("getdone` distribution name is already occupied", text)
        self.assertIn("import getdone", text)
        nav = (ROOT / "zensical.toml").read_text(encoding="utf-8")
        self.assertIn("reference/package-naming.md", nav)


if __name__ == "__main__":
    unittest.main()
