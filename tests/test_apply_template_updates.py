from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from getdone.apply_template_updates import apply_template_updates
from getdone.initialise_project import initialise_project
from getdone.template_updates import inspect_template_updates


class ApplyTemplateUpdatesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository_root = Path(__file__).resolve().parents[1]
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.skills_root = Path(self.temp_dir.name) / "skills"
        shutil.copytree(
            self.repository_root,
            self.skills_root,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        self.project_root = Path(self.temp_dir.name) / "project"
        initialise_project(self.project_root, "standard", skills_root=self.skills_root)

    def _upgrade_source(self, relative: str) -> None:
        source = self.skills_root / "skill/bootstrap" / "templates" / "standard" / relative
        source.write_text(
            source.read_text(encoding="utf-8").replace(
                "template_version: 2.0.0", "template_version: 2.1.0"
            )
            + "\n## Added by migration\n",
            encoding="utf-8",
        )

    def test_default_application_is_a_dry_run(self) -> None:
        target = self.project_root / ".agent" / "tracking" / "risks.md"
        target.unlink()

        result = apply_template_updates(
            self.project_root,
            skills_root=self.skills_root,
        )

        self.assertFalse(target.exists())
        self.assertEqual(result.added, ())
        self.assertEqual(result.replaced, ())
        self.assertTrue(result.dry_run)

    def test_additions_and_replacements_require_separate_authorisation(self) -> None:
        missing = self.project_root / ".agent" / "tracking" / "risks.md"
        missing.unlink()
        relative_update = ".agent/current/task.md"
        self._upgrade_source(relative_update)
        installed = self.project_root / relative_update
        before = installed.read_text(encoding="utf-8")

        additions = apply_template_updates(
            self.project_root,
            skills_root=self.skills_root,
            apply_additions=True,
        )

        self.assertTrue(missing.is_file())
        self.assertEqual(installed.read_text(encoding="utf-8"), before)
        self.assertIn(Path(".agent/tracking/risks.md"), additions.added)
        self.assertNotIn(Path(relative_update), additions.replaced)

        replacements = apply_template_updates(
            self.project_root,
            skills_root=self.skills_root,
            apply_replacements=True,
        )

        self.assertIn(Path(relative_update), replacements.replaced)
        self.assertIn("Added by migration", installed.read_text(encoding="utf-8"))

    def test_profile_metadata_waits_for_required_additions(self) -> None:
        minimal_project = Path(self.temp_dir.name) / "metadata-guard-project"
        initialise_project(minimal_project, "minimal", skills_root=self.skills_root)

        result = apply_template_updates(
            minimal_project,
            skills_root=self.skills_root,
            profile="standard",
            apply_replacements=True,
        )

        reference = (minimal_project / ".agent" / "skills-reference.md").read_text(
            encoding="utf-8"
        )
        self.assertIn('bootstrap_profile: "minimal"', reference)
        self.assertIn(Path(".agent/skills-reference.md"), result.skipped)

    def test_profile_change_adds_child_files_and_updates_profile_metadata(self) -> None:
        minimal_project = Path(self.temp_dir.name) / "minimal-project"
        initialise_project(minimal_project, "minimal", skills_root=self.skills_root)

        additions = apply_template_updates(
            minimal_project,
            skills_root=self.skills_root,
            profile="standard",
            apply_additions=True,
        )

        self.assertTrue((minimal_project / ".agent" / "tracking" / "todos.md").is_file())
        self.assertIn(Path(".agent/tracking/todos.md"), additions.added)
        reference_before = (minimal_project / ".agent" / "skills-reference.md").read_text(
            encoding="utf-8"
        )
        self.assertIn('bootstrap_profile: "minimal"', reference_before)

        replacements = apply_template_updates(
            minimal_project,
            skills_root=self.skills_root,
            profile="standard",
            apply_replacements=True,
        )

        reference_after = (minimal_project / ".agent" / "skills-reference.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(Path(".agent/skills-reference.md"), replacements.replaced)
        self.assertIn('bootstrap_profile: "standard"', reference_after)
        self.assertIn(
            'bootstrap_profile_version: "1.7.0"',
            reference_after,
        )

    def test_modified_project_file_is_never_replaced(self) -> None:
        relative = ".agent/current/task.md"
        self._upgrade_source(relative)
        target = self.project_root / relative
        target.write_text(
            target.read_text(encoding="utf-8") + "\nProject decision.\n",
            encoding="utf-8",
        )
        before = target.read_text(encoding="utf-8")

        result = apply_template_updates(
            self.project_root,
            skills_root=self.skills_root,
            apply_additions=True,
            apply_replacements=True,
        )

        self.assertEqual(target.read_text(encoding="utf-8"), before)
        self.assertNotIn(Path(relative), result.replaced)
        self.assertIn(Path(relative), result.skipped)

    def test_plan_contains_unified_diffs_for_actionable_files(self) -> None:
        missing = self.project_root / ".agent" / "tracking" / "risks.md"
        missing.unlink()
        relative_update = ".agent/current/task.md"
        self._upgrade_source(relative_update)

        updates = inspect_template_updates(self.project_root, skills_root=self.skills_root)
        missing_result = next(
            item
            for item in updates
            if item.path == Path(".agent/tracking/risks.md")
        )
        update_result = next(item for item in updates if item.path == Path(relative_update))

        self.assertIn("--- /dev/null", missing_result.diff)
        self.assertIn("+++ b/.agent/tracking/risks.md", missing_result.diff)
        self.assertIn("--- a/.agent/current/task.md", update_result.diff)
        self.assertIn("+++ b/.agent/current/task.md", update_result.diff)


if __name__ == "__main__":
    unittest.main()
