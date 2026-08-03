from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from getdone.apply_template_updates import main as migrate_main
from getdone.check_template_updates import main as check_main
from getdone.initialise_project import initialise_project


class SectionSuggestionCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skills_root = Path(__file__).resolve().parents[1]
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.project_root = Path(self.temp_dir.name) / "project"
        initialise_project(self.project_root, "minimal", skills_root=self.skills_root)
        self.target = self.project_root / ".agent" / "current" / "next-step.md"
        self.target.write_text(
            self.target.read_text(encoding="utf-8").replace(
                "## Validation",
                "## Verification\n\nUse project checks.\n\n## Validation",
            ),
            encoding="utf-8",
        )

    def test_check_json_includes_section_suggestions(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            code = check_main(
                [
                    "--project-root",
                    str(self.project_root),
                    "--skills-root",
                    str(self.skills_root),
                    "--json",
                ]
            )

        payload = json.loads(output.getvalue())
        result = next(item for item in payload if item["path"] == ".agent/current/next-step.md")
        self.assertEqual(code, 0)
        self.assertTrue(result["merge_suggestion"]["available"])
        self.assertGreater(result["merge_suggestion"]["summary"]["removed"], 0)

    def test_human_output_requires_sections_flag(self) -> None:
        plain = io.StringIO()
        with redirect_stdout(plain):
            check_main(
                [
                    "--project-root",
                    str(self.project_root),
                    "--skills-root",
                    str(self.skills_root),
                ]
            )
        detailed = io.StringIO()
        with redirect_stdout(detailed):
            check_main(
                [
                    "--project-root",
                    str(self.project_root),
                    "--skills-root",
                    str(self.skills_root),
                    "--sections",
                ]
            )

        self.assertNotIn("section-summary:", plain.getvalue())
        self.assertIn("section-summary:", detailed.getvalue())
        self.assertIn("no project files were modified", detailed.getvalue())

    def test_migration_sections_remain_read_only_for_modified_files(self) -> None:
        before = self.target.read_text(encoding="utf-8")
        output = io.StringIO()
        with redirect_stdout(output):
            code = migrate_main(
                [
                    "--project-root",
                    str(self.project_root),
                    "--skills-root",
                    str(self.skills_root),
                    "--sections",
                    "--no-diff",
                    "--apply-replacements",
                ]
            )

        self.assertEqual(code, 0)
        self.assertIn("section-summary:", output.getvalue())
        self.assertEqual(self.target.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
