from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from getdone.frontmatter import parse_frontmatter, verify_template_digest
from getdone.initialise_project import initialise_project
from getdone.template_updates import inspect_template_updates


class TemplateLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skills_root = Path(__file__).resolve().parents[1]
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.project_root = Path(self.temp_dir.name) / "example-project"

    def test_initialisation_adds_verifiable_template_digests(self) -> None:
        initialise_project(
            self.project_root,
            "standard",
            skills_root=self.skills_root,
            skills_reference="../getdone",
        )

        managed = self.project_root / ".agent" / "current" / "next-step.md"
        document = parse_frontmatter(managed.read_text(encoding="utf-8"))

        self.assertEqual(document.data["template"], "next-step")
        self.assertIn("template_digest", document.data)
        self.assertTrue(verify_template_digest(managed.read_text(encoding="utf-8")))

    def test_fresh_project_has_no_template_updates(self) -> None:
        initialise_project(self.project_root, "standard", skills_root=self.skills_root)

        updates = inspect_template_updates(
            self.project_root,
            skills_root=self.skills_root,
        )

        self.assertTrue(updates)
        self.assertEqual({item.status for item in updates}, {"current"})

    def test_modified_project_file_is_never_classified_as_safe_update(self) -> None:
        initialise_project(self.project_root, "standard", skills_root=self.skills_root)
        target = self.project_root / ".agent" / "current" / "next-step.md"
        target.write_text(
            target.read_text(encoding="utf-8") + "\nProject-specific note.\n",
            encoding="utf-8",
        )

        updates = inspect_template_updates(
            self.project_root,
            skills_root=self.skills_root,
        )
        result = next(item for item in updates if item.path == Path(".agent/current/next-step.md"))

        self.assertEqual(result.status, "modified")
        self.assertFalse(result.safe_to_replace)

    def test_missing_template_file_is_reported_as_safe_addition(self) -> None:
        initialise_project(self.project_root, "standard", skills_root=self.skills_root)
        target = self.project_root / ".agent" / "tracking" / "risks.md"
        target.unlink()

        updates = inspect_template_updates(
            self.project_root,
            skills_root=self.skills_root,
        )
        result = next(item for item in updates if item.path == Path(".agent/tracking/risks.md"))

        self.assertEqual(result.status, "missing")
        self.assertTrue(result.safe_to_add)

    def test_newer_source_template_is_reported_without_modifying_project(self) -> None:
        copied_skills = Path(self.temp_dir.name) / "skills-copy"
        shutil.copytree(
            self.skills_root,
            copied_skills,
            ignore=shutil.ignore_patterns(".git", "__pycache__"),
        )
        initialise_project(self.project_root, "minimal", skills_root=copied_skills)

        source = (
            copied_skills
            / "skill/bootstrap"
            / "templates"
            / "minimal"
            / ".agent"
            / "current"
            / "next-step.md"
        )
        before_project = (self.project_root / ".agent" / "current" / "next-step.md").read_text(
            encoding="utf-8"
        )
        updated_source = source.read_text(encoding="utf-8").replace(
            "template_version: 3.0.0", "template_version: 3.1.0"
        )
        source.write_text(updated_source + "\n## Upgrade-only section\n", encoding="utf-8")

        updates = inspect_template_updates(self.project_root, skills_root=copied_skills)
        result = next(item for item in updates if item.path == Path(".agent/current/next-step.md"))

        self.assertEqual(result.status, "update-available")
        self.assertEqual(result.installed_version, "3.0.0")
        self.assertEqual(result.available_version, "3.1.0")
        self.assertTrue(result.safe_to_replace)
        self.assertEqual(
            (self.project_root / ".agent" / "current" / "next-step.md").read_text(
                encoding="utf-8"
            ),
            before_project,
        )

    def test_modified_markdown_includes_read_only_section_suggestions(self) -> None:
        initialise_project(self.project_root, "minimal", skills_root=self.skills_root)
        target = self.project_root / ".agent" / "current" / "next-step.md"
        target.write_text(
            target.read_text(encoding="utf-8").replace(
                "## Validation",
                "## Verification\n\nProject-specific validation detail.\n\n## Validation",
            ),
            encoding="utf-8",
        )
        before = target.read_text(encoding="utf-8")

        updates = inspect_template_updates(self.project_root, skills_root=self.skills_root)
        result = next(item for item in updates if item.path == Path(".agent/current/next-step.md"))

        self.assertEqual(result.status, "modified")
        self.assertIsNotNone(result.merge_suggestion)
        assert result.merge_suggestion is not None
        self.assertEqual(result.merge_suggestion.summary["removed"], 1)
        self.assertEqual(target.read_text(encoding="utf-8"), before)
        self.assertIn("merge_suggestion", result.as_dict())

    def test_update_results_are_json_serialisable(self) -> None:
        initialise_project(self.project_root, "minimal", skills_root=self.skills_root)
        updates = inspect_template_updates(self.project_root, skills_root=self.skills_root)

        json.dumps([item.as_dict() for item in updates])


if __name__ == "__main__":
    unittest.main()
