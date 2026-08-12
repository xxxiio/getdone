from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from getdone.initialise_project import build_parser, initialise_project, main as initialise_main


class InitialiseProjectTests(unittest.TestCase):
    def test_standard_profile_creates_project_local_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = initialise_project(root, "standard")

            self.assertTrue((root / "AGENTS.md").is_file())
            self.assertTrue((root / ".agent" / "current" / "next-step.md").is_file())
            self.assertTrue((root / ".agent" / "tracking" / "todos.md").is_file())
            self.assertIn(Path("AGENTS.md"), result.created)
            self.assertEqual((), result.skipped)

    def test_existing_project_files_are_not_overwritten_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / ".agent" / "current" / "next-step.md"
            target.parent.mkdir(parents=True)
            target.write_text("project-owned content\n", encoding="utf-8")

            result = initialise_project(root, "standard")

            self.assertEqual("project-owned content\n", target.read_text(encoding="utf-8"))
            self.assertIn(Path(".agent/current/next-step.md"), result.skipped)

    def test_unknown_profile_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                initialise_project(Path(directory), "unknown")

    def test_cli_accepts_explicit_skills_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory) / "cli-project"

            code = initialise_main(
                [
                    "--project-root",
                    str(project_root),
                    "--skills-root",
                    str(Path(__file__).resolve().parents[1]),
                ]
            )

            self.assertEqual(code, 0)
            self.assertTrue((project_root / ".agent" / "skills-reference.md").is_file())
            self.assertTrue((project_root / ".agent" / "tracking" / "todos.md").is_file())

    def test_public_cli_defaults_project_root_and_hides_profile_option(self) -> None:
        args = build_parser().parse_args([])

        self.assertEqual(Path.cwd(), args.project_root)
        self.assertNotIn("--profile", build_parser().format_help())


class TemplateRenderingTests(unittest.TestCase):
    def test_bootstrap_renders_project_and_skills_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            initialise_project(root, "standard", project_name="Example Project")

            reference = (root / ".agent" / "skills-reference.md").read_text(encoding="utf-8")
            context = (root / ".agent" / "project-context.md").read_text(encoding="utf-8")

            self.assertIn("Example Project", context)
            self.assertIn("getdone", reference)
            self.assertIn('bootstrap_profile_version: "1.7.0"', reference)
            self.assertIn('bootstrap_profile_lineage: "minimal -> standard"', reference)
            self.assertNotIn("{{", reference)
            self.assertNotIn("{{", context)


if __name__ == "__main__":
    unittest.main()
