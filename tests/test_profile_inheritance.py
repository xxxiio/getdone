from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from getdone.initialise_project import initialise_project
from getdone.profiles import collect_profile_templates, load_profiles, resolve_profile


_TEMPLATE = """---
template: {template}
template_version: 1.0.0
project_owned: true
---

{body}
"""


class ProfileInheritanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.skills_root = Path(self.temp_dir.name) / "skills"
        (self.skills_root / "skill/bootstrap" / "templates").mkdir(parents=True)
        (self.skills_root / "VERSION").write_text("9.9.9\n", encoding="utf-8")
        repository = Path(__file__).resolve().parents[1]
        for relative in (
            "AGENTS.md",
            "skill/START-HERE.md",
            "skill/registry/workflows.json",
            "skill/registry/reuse-catalogue.json",
            "skill/adapters/manifest.json",
            "skill/schemas/skills-lock.schema.json",
        ):
            source = repository / relative
            target = self.skills_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    def _write_profile_file(self, profile: str, relative: str, body: str) -> None:
        target = self.skills_root / "skill/bootstrap" / "templates" / profile / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            _TEMPLATE.format(template=Path(relative).stem, body=body),
            encoding="utf-8",
        )

    def _write_manifest(self, profiles: dict[str, object]) -> None:
        manifest = {"schema_version": 1, "profiles": profiles}
        path = self.skills_root / "skill/bootstrap" / "manifests.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")

    def test_child_profile_inherits_parent_and_overrides_matching_paths(self) -> None:
        self._write_manifest(
            {
                "base": {
                    "version": "1.0.0",
                    "description": "base",
                    "source": "skill/bootstrap/templates/base",
                },
                "team": {
                    "version": "1.0.0",
                    "description": "team",
                    "extends": ["base"],
                    "source": "skill/bootstrap/templates/team",
                },
            }
        )
        self._write_profile_file("base", ".agent/base.md", "base file")
        self._write_profile_file("base", ".agent/shared.md", "base shared")
        self._write_profile_file("team", ".agent/team.md", "team file")
        self._write_profile_file("team", ".agent/shared.md", "team shared")

        project_root = Path(self.temp_dir.name) / "project"
        initialise_project(project_root, "team", skills_root=self.skills_root)

        self.assertTrue((project_root / ".agent" / "base.md").is_file())
        self.assertTrue((project_root / ".agent" / "team.md").is_file())
        self.assertIn(
            "team shared",
            (project_root / ".agent" / "shared.md").read_text(encoding="utf-8"),
        )

    def test_profile_resolution_is_parent_first_and_deduplicated(self) -> None:
        self._write_manifest(
            {
                "base": {
                    "version": "1.0.0",
                    "description": "base",
                    "source": "skill/bootstrap/templates/base",
                },
                "left": {
                    "version": "1.0.0",
                    "description": "left",
                    "extends": ["base"],
                },
                "right": {
                    "version": "1.0.0",
                    "description": "right",
                    "extends": ["base"],
                },
                "combined": {
                    "version": "1.0.0",
                    "description": "combined",
                    "extends": ["left", "right"],
                },
            }
        )

        resolved = resolve_profile(load_profiles(self.skills_root), "combined")

        self.assertEqual(resolved.lineage, ("base", "left", "right", "combined"))

    def test_profile_cycle_is_rejected(self) -> None:
        self._write_manifest(
            {
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
            }
        )

        with self.assertRaisesRegex(ValueError, "cycle"):
            resolve_profile(load_profiles(self.skills_root), "one")

    def test_repository_standard_profile_inherits_minimal(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        profiles = load_profiles(repository_root)
        resolved = resolve_profile(profiles, "standard")
        templates = collect_profile_templates(repository_root, resolved)

        self.assertEqual(resolved.lineage, ("minimal", "standard"))
        self.assertIn(Path(".agent/current/next-step.md"), templates)
        self.assertIn(Path(".agent/tracking/todos.md"), templates)


if __name__ == "__main__":
    unittest.main()
