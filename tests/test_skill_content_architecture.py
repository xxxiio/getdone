from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SkillProductBoundaryTests(unittest.TestCase):
    def test_canonical_product_has_one_physical_root(self) -> None:
        self.assertTrue((ROOT / "skill/START-HERE.md").is_file())
        self.assertTrue((ROOT / "skill/workflows").is_dir())
        self.assertTrue((ROOT / "skill/standards").is_dir())
        self.assertTrue((ROOT / "skill/acceptance").is_dir())
        self.assertFalse((ROOT / "skills").exists())
        self.assertFalse((ROOT / "best-practices").exists())
        self.assertFalse((ROOT / "acceptance").exists())

    def test_product_markdown_links_stay_inside_product(self) -> None:
        from development.tools.validate_repository import validate_product_links_stay_inside_skill

        self.assertEqual([], validate_product_links_stay_inside_skill(ROOT))

    def test_normal_context_uses_no_more_than_eight_product_documents(self) -> None:
        from getdone.context_selection import select_context

        for task_class in ("feature", "bug-fix", "refactoring", "investigation"):
            for language in ("python", "cpp", "rust", "q-kdbplus", "dart-flutter", "typescript"):
                with self.subTest(task_class=task_class, language=language):
                    selection = select_context(ROOT, task_class, language)
                    self.assertLessEqual(len(selection.documents), 8)
                    self.assertTrue(all(path.startswith("skill/") for path in selection.documents))

    def test_rc2_context_is_at_least_twenty_percent_smaller_than_rc1(self) -> None:
        from getdone.context_selection import select_context

        rc1_tokens = {
            "feature": 4915,
            "bug-fix": 4894,
            "refactoring": 4874,
            "investigation": 4825,
        }
        for task_class, baseline in rc1_tokens.items():
            selection = select_context(ROOT, task_class, "python")
            self.assertLessEqual(selection.approximate_tokens, int(baseline * 0.8))


    def test_product_contains_usage_guide(self) -> None:
        usage = ROOT / "skill/USAGE.md"
        self.assertTrue(usage.is_file())
        text = usage.read_text(encoding="utf-8")
        self.assertIn("## Start a task", text)
        self.assertIn("## Project record authority", text)
        self.assertIn("## Maintain the skill repository", text)

    def test_skill_pack_contains_only_product_content(self) -> None:
        from development.tools.build_skill_pack import build_skill_pack

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "skill-pack.zip"
            build_skill_pack(ROOT, output)
            with zipfile.ZipFile(output) as archive:
                names = set(archive.namelist())

        self.assertIn("skill/START-HERE.md", names)
        self.assertIn("VERSION", names)
        self.assertNotIn("getdone/context_selection.py", names)
        self.assertNotIn("tests/test_context_selection.py", names)
        self.assertTrue(all(name == "VERSION" or name.startswith("skill/") for name in names))

    def test_skill_pack_supports_bootstrap_and_project_validation(self) -> None:
        from development.tools.build_skill_pack import build_skill_pack
        from getdone.initialise_project import initialise_project
        from getdone.validate_project import validate_project

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive_path = root / "skill-pack.zip"
            extracted = root / "pack"
            project = root / "project"
            build_skill_pack(ROOT, archive_path)
            with zipfile.ZipFile(archive_path) as archive:
                archive.extractall(extracted)
            project.mkdir()

            initialise_project(
                project,
                "standard",
                skills_root=extracted,
                skills_reference=".getdone",
            )
            report = validate_project(project, skills_root=extracted)

        self.assertTrue(report.is_valid, report.errors)


class SkillDocumentContractTests(unittest.TestCase):
    def test_canonical_documents_are_operational(self) -> None:
        from development.tools.validate_skill_content import validate_skill_content

        self.assertEqual([], validate_skill_content(ROOT))

    def test_vague_workflow_is_rejected(self) -> None:
        from development.tools.validate_skill_content import validate_workflow_text

        errors = validate_workflow_text("# Vague\n\nDo good work.\n")
        self.assertTrue(errors)
        self.assertTrue(any("Use this when" in error for error in errors))

    def test_vague_policy_is_rejected(self) -> None:
        from development.tools.validate_skill_content import validate_policy_text

        errors = validate_policy_text("# Policy\n\nBe careful.\n")
        self.assertTrue(errors)
        self.assertTrue(any("Applies when" in error for error in errors))

    def test_recurring_workflows_use_task_specific_evidence(self) -> None:
        general = (
            ROOT / "skill/workflows/general/deterministic-development.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("proportionate baseline", general)
        for phrase in (
            "declared test-tier baseline",
            "failing behavioural or regression evidence",
            "characterisation evidence",
            "experiment or source inspection",
            "unavailable proof, alternative evidence, and resulting limitation",
        ):
            self.assertIn(phrase, general)

        feature = (ROOT / "skill/workflows/feature/tdd-feature-development.md").read_text(
            encoding="utf-8"
        )
        bug_fix = (
            ROOT / "skill/workflows/bug-fix/regression-first-bug-fix.md"
        ).read_text(encoding="utf-8")
        refactoring = (
            ROOT / "skill/workflows/refactoring/characterisation-first-refactoring.md"
        ).read_text(encoding="utf-8")
        self.assertIn("declared in the task acceptance criteria or change-impact record", feature)
        self.assertIn("named in the task or change-impact record", bug_fix)
        self.assertIn("must change together", refactoring)

    def test_change_type_waivers_name_alternative_evidence_and_risk(self) -> None:
        for path in sorted((ROOT / "skill/acceptance/change-types").glob("*.md")):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("unavailable primary evidence", text)
                self.assertIn("alternative evidence", text)
                self.assertIn("residual risk", text)


if __name__ == "__main__":
    unittest.main()
