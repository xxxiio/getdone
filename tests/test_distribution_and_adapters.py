from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from getdone.initialise_project import initialise_project

ROOT = Path(__file__).resolve().parents[1]


class AdapterContractTests(unittest.TestCase):
    def test_adapter_repository_satisfies_contract(self) -> None:
        from getdone.adapters import validate_adapter_repository

        self.assertEqual([], validate_adapter_repository(ROOT))

    def test_repository_validation_includes_adapter_contracts(self) -> None:
        from development.tools.validate_repository import validate_repository

        self.assertEqual([], validate_repository(ROOT))


class AdapterInstallationTests(unittest.TestCase):
    def test_cli_lists_adapters_without_project(self) -> None:
        from getdone.install_adapter import main

        self.assertEqual(0, main(["--skills-root", str(ROOT), "--list"]))

    def _bootstrapped_project(self, root: Path) -> Path:
        project = root / "project"
        initialise_project(project, "minimal", skills_root=ROOT)
        return project

    def test_installs_claude_adapter_without_overwriting_project_state(self) -> None:
        from getdone.install_adapter import install_adapter

        with tempfile.TemporaryDirectory() as directory:
            project = self._bootstrapped_project(Path(directory))

            result = install_adapter(project, "claude", skills_root=ROOT)

            target = project / "CLAUDE.md"
            self.assertEqual("created", result.status)
            self.assertEqual(Path("CLAUDE.md"), result.path)
            text = target.read_text(encoding="utf-8")
            self.assertIn("AGENTS.md", text)
            self.assertIn(".agent/skills-reference.md", text)
            self.assertIn("skill/workflow-router.md", text)

            target.write_text("project-owned\n", encoding="utf-8")
            second = install_adapter(project, "claude", skills_root=ROOT)
            self.assertEqual("skipped", second.status)
            self.assertEqual("project-owned\n", target.read_text(encoding="utf-8"))

    def test_installs_nested_cursor_and_copilot_adapters(self) -> None:
        from getdone.install_adapter import install_adapter

        with tempfile.TemporaryDirectory() as directory:
            project = self._bootstrapped_project(Path(directory))

            cursor = install_adapter(project, "cursor", skills_root=ROOT)
            copilot = install_adapter(project, "github-copilot", skills_root=ROOT)

            self.assertEqual(Path(".cursor/rules/getdone.mdc"), cursor.path)
            self.assertEqual(Path(".github/copilot-instructions.md"), copilot.path)
            self.assertTrue((project / cursor.path).is_file())
            self.assertTrue((project / copilot.path).is_file())

    def test_reference_only_adapters_do_not_create_files(self) -> None:
        from getdone.install_adapter import install_adapter

        with tempfile.TemporaryDirectory() as directory:
            project = self._bootstrapped_project(Path(directory))

            chatgpt = install_adapter(project, "chatgpt", skills_root=ROOT)
            codex = install_adapter(project, "codex", skills_root=ROOT)

            self.assertEqual("reference-only", chatgpt.status)
            self.assertEqual("bootstrap-managed", codex.status)
            self.assertIsNone(chatgpt.path)
            self.assertEqual(Path("AGENTS.md"), codex.path)

    def test_adapter_install_requires_bootstrapped_project(self) -> None:
        from getdone.install_adapter import install_adapter

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                install_adapter(Path(directory), "claude", skills_root=ROOT)


class ProjectValidationTests(unittest.TestCase):
    def test_fresh_project_is_valid_and_modified_state_is_allowed(self) -> None:
        from getdone.validate_project import validate_project

        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            initialise_project(project, "standard", skills_root=ROOT)
            report = validate_project(project, skills_root=ROOT)
            self.assertTrue(report.is_valid)
            self.assertEqual((), report.errors)

            next_step = project / ".agent/current/next-step.md"
            next_step.write_text(
                next_step.read_text(encoding="utf-8") + "\n- Local plan.\n",
                encoding="utf-8",
            )
            modified_report = validate_project(project, skills_root=ROOT)
            self.assertTrue(modified_report.is_valid)
            self.assertTrue(
                any("modified" in warning.message for warning in modified_report.warnings)
            )

    def test_invalid_controlled_record_is_invalid(self) -> None:
        from getdone.validate_project import validate_project

        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            initialise_project(project, "minimal", skills_root=ROOT)
            next_step = project / ".agent/current/next-step.md"
            text = next_step.read_text(encoding="utf-8").replace(
                "status: proposed", "status: ready"
            )
            next_step.write_text(text, encoding="utf-8")

            report = validate_project(project, skills_root=ROOT)

            self.assertFalse(report.is_valid)
            self.assertTrue(
                any("placeholder" in error.message for error in report.errors)
            )

    def test_missing_composition_lock_is_invalid(self) -> None:
        from getdone.composition_lock import LOCK_PATH
        from getdone.validate_project import validate_project

        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            initialise_project(project, "minimal", skills_root=ROOT)
            (project / LOCK_PATH).unlink()

            report = validate_project(project, skills_root=ROOT)

            self.assertFalse(report.is_valid)
            self.assertTrue(any(error.path == LOCK_PATH for error in report.errors))

    def test_missing_managed_file_is_invalid(self) -> None:
        from getdone.validate_project import validate_project

        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            initialise_project(project, "minimal", skills_root=ROOT)
            (project / ".agent/current/next-step.md").unlink()

            report = validate_project(project, skills_root=ROOT)

            self.assertFalse(report.is_valid)
            self.assertTrue(any("missing" in error.message for error in report.errors))


class ExampleConsumingProjectTests(unittest.TestCase):
    def test_example_bootstraps_installs_adapters_and_runs_tests(self) -> None:
        from getdone.install_adapter import install_adapter
        from getdone.validate_project import validate_project

        source = ROOT / "examples/minimal-consuming-project"
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "example"
            shutil.copytree(source, project)
            overlay = (
                ROOT
                / "skill/references/examples/organisation-catalogue-overlay/registry-overlay.json"
            )
            initialise_project(
                project,
                "standard",
                skills_root=ROOT,
                overlay_paths=(overlay,),
            )
            for adapter in ("claude", "cursor", "github-copilot"):
                install_adapter(project, adapter, skills_root=ROOT)

            report = validate_project(project, skills_root=ROOT)
            self.assertTrue(report.is_valid)
            self.assertEqual(("org.example@1.0.0",), report.overlay_versions)
            completed = subprocess.run(
                [sys.executable, "-m", "pytest", "tests"],
                cwd=project,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            self.assertFalse((ROOT / ".agent").exists())


if __name__ == "__main__":
    unittest.main()
