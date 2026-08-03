from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from development.tools.validate_frontmatter import (
    validate_bootstrap_template_files,
    validate_bootstrap_manifest,
    validate_document_against_schema,
    validate_workflow_files,
)


class FrontmatterValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository_root = Path(__file__).resolve().parents[1]

    def test_repository_workflows_match_schema(self) -> None:
        errors = validate_workflow_files(self.repository_root)
        self.assertEqual(errors, [])

    def test_bootstrap_templates_match_schema(self) -> None:
        errors = validate_bootstrap_template_files(self.repository_root)
        self.assertEqual(errors, [])

    def test_bootstrap_manifest_matches_schema(self) -> None:
        errors = validate_bootstrap_manifest(self.repository_root)
        self.assertEqual(errors, [])

    def test_profile_inheritance_cycle_is_rejected_by_manifest_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "skill/schemas").mkdir(parents=True)
            (root / "skill/bootstrap").mkdir(parents=True)
            schema = (
                self.repository_root
                / "skill/schemas/bootstrap-manifest.schema.json"
            ).read_text(encoding="utf-8")
            (root / "skill/schemas" / "bootstrap-manifest.schema.json").write_text(
                schema, encoding="utf-8"
            )
            manifest = {
                "schema_version": 1,
                "profiles": {
                    "one": {
                        "version": "1.0.0",
                        "description": "one",
                        "extends": ["two"],
                    },
                    "two": {
                        "version": "1.0.0",
                        "description": "two",
                        "extends": ["one"],
                    },
                },
            }
            (root / "skill/bootstrap" / "manifests.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )

            errors = validate_bootstrap_manifest(root)

            self.assertTrue(errors)
            self.assertIn("cycle", errors[0])

    def test_invalid_workflow_status_is_rejected(self) -> None:
        schema = json.loads(
            (self.repository_root / "skill/schemas" / "workflow-frontmatter.schema.json").read_text(
                encoding="utf-8"
            )
        )
        text = """---
id: workflow.example.invalid
version: 1.0.0
status: unknown
---

# Invalid
"""

        errors = validate_document_against_schema(text, schema)

        self.assertTrue(errors)
        self.assertIn("status", errors[0])

    def test_missing_frontmatter_is_rejected(self) -> None:
        schema = json.loads(
            (self.repository_root / "skill/schemas" / "workflow-frontmatter.schema.json").read_text(
                encoding="utf-8"
            )
        )

        errors = validate_document_against_schema("# No front matter\n", schema)

        self.assertEqual(errors, ["document has no YAML front matter"])

    def test_every_workflow_declares_required_outputs(self) -> None:
        import yaml

        for path in sorted((self.repository_root / "skill/workflows").rglob("*.md")):
            with self.subTest(path=path.relative_to(self.repository_root)):
                payload = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
                self.assertTrue(payload.get("required_outputs"))



if __name__ == "__main__":
    unittest.main()
