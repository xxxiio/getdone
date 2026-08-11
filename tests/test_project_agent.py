from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from getdone.project_agent import (
    ProjectAgentError,
    infer_affected_languages,
    select_project_agent,
    validate_project_agent,
)


class ProjectAgentTests(unittest.TestCase):
    def _project(self, root: Path) -> Path:
        agent = root / ".project-agent"
        (agent / "implementation/app").mkdir(parents=True)
        (agent / "capabilities").mkdir(parents=True)
        (agent / "AGENTS.md").write_text("# Project baseline\n", encoding="utf-8")
        (agent / "implementation/app/gui.md").write_text("# GUI\n", encoding="utf-8")
        (agent / "capabilities/forms.md").write_text("# Forms\n", encoding="utf-8")
        index = {
            "schema_version": 1,
            "language_patterns": {
                "dart-flutter": ["applications/**/*.dart"],
                "python": ["tooling/**/*.py"],
            },
            "infer": [
                {
                    "paths": ["applications/**/view/**"],
                    "concerns": ["gui"],
                }
            ],
            "rules": [
                {
                    "id": "app-gui",
                    "paths": ["applications/**"],
                    "concerns": ["gui"],
                    "load": ["implementation/app/gui.md"],
                },
                {
                    "id": "forms",
                    "concerns": ["forms"],
                    "load": ["capabilities/forms.md"],
                },
            ],
        }
        (agent / "index.json").write_text(json.dumps(index), encoding="utf-8")
        return root

    def test_health_validates_complete_extension(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._project(Path(directory))
            report = validate_project_agent(root)
            self.assertTrue(report.is_valid)
            self.assertEqual(2, report.rule_count)
            self.assertEqual(1, report.inference_count)
            self.assertEqual(2, report.referenced_files)

    def test_selection_always_loads_agents_and_routes_bounded_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._project(Path(directory))
            selection = select_project_agent(
                root,
                changed_paths=["applications/demo/view/page.dart"],
            )
            assert selection is not None
            self.assertEqual(
                (
                    ".project-agent/AGENTS.md",
                    ".project-agent/implementation/app/gui.md",
                ),
                selection.documents,
            )
            self.assertEqual(("gui",), selection.inferred_concerns)
            self.assertEqual(("app-gui",), selection.matched_rules)
            self.assertEqual(("dart-flutter",), selection.affected_languages)

    def test_explicit_and_inferred_languages_compose(self) -> None:
        languages = infer_affected_languages(
            ["lib/main.dart", "tooling/build.py"],
            explicit_languages=["rust"],
        )
        self.assertEqual(("rust", "python", "dart-flutter"), languages)

    def test_missing_reference_is_unhealthy_and_not_selectable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._project(Path(directory))
            (root / ".project-agent/implementation/app/gui.md").unlink()
            report = validate_project_agent(root)
            self.assertFalse(report.is_valid)
            with self.assertRaises(ProjectAgentError):
                select_project_agent(
                    root,
                    changed_paths=["applications/demo/view/page.dart"],
                )


if __name__ == "__main__":
    unittest.main()
