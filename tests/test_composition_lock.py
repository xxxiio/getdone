from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from getdone.composition_lock import (
    LOCK_PATH,
    assess_lock,
    build_lock_payload,
    classify_version_change,
    load_lockfile,
)
from getdone.initialise_project import initialise_project
from getdone.manage_composition_lock import main as lock_main

ROOT = Path(__file__).resolve().parents[1]


class CompositionLockTests(unittest.TestCase):
    def test_bootstrap_creates_schema_valid_lock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            initialise_project(project, "standard", skills_root=ROOT)

            payload = load_lockfile(project / LOCK_PATH, ROOT)

            self.assertEqual("standard", payload["profile"]["name"])
            self.assertEqual(["minimal", "standard"], payload["profile"]["lineage"])
            self.assertEqual([], payload["overlays"])
            self.assertEqual(
                (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
                payload["core"]["version"],
            )
            self.assertEqual("current", assess_lock(project, ROOT).status)

    def test_overlay_documents_are_pinned_with_the_overlay(self) -> None:
        overlay = (
            ROOT
            / "skill/references/examples/organisation-catalogue-overlay/registry-overlay.json"
        )
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            project.mkdir()
            payload = build_lock_payload(
                project,
                ROOT,
                "minimal",
                overlay_paths=(overlay,),
            )

            self.assertEqual(1, len(payload["overlays"]))
            self.assertEqual("org.example", payload["overlays"][0]["source"])
            self.assertEqual("1.0.0", payload["overlays"][0]["version"])

    def test_overlay_location_does_not_change_composition_digest(self) -> None:
        source = ROOT / "skill/references/examples/organisation-catalogue-overlay"
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            project_one = workspace / "one"
            project_two = workspace / "two"
            copied_overlay = project_two / "guidance"
            shutil.copytree(source, copied_overlay)
            first = build_lock_payload(
                project_one,
                ROOT,
                "minimal",
                overlay_paths=(source / "registry-overlay.json",),
            )
            second = build_lock_payload(
                project_two,
                ROOT,
                "minimal",
                overlay_paths=(copied_overlay / "registry-overlay.json",),
            )

            self.assertNotEqual(
                first["overlays"][0]["reference"],
                second["overlays"][0]["reference"],
            )
            self.assertEqual(first["composition_digest"], second["composition_digest"])

    def test_same_version_content_change_is_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            project = workspace / "project"
            copied_skills = workspace / "skills"
            initialise_project(project, "minimal", skills_root=ROOT)
            shutil.copytree(
                ROOT,
                copied_skills,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            start_here = copied_skills / "skill/START-HERE.md"
            start_here.write_text(
                start_here.read_text(encoding="utf-8") + "\nUnexpected same-version edit.\n",
                encoding="utf-8",
            )

            assessment = assess_lock(project, copied_skills)

            self.assertEqual("incompatible", assessment.status)
            self.assertTrue(
                any(
                    item.component == "core" and item.status == "drift"
                    for item in assessment.findings
                )
            )

    def test_rewrite_preserves_locked_overlays_when_flags_are_omitted(self) -> None:
        overlay = (
            ROOT
            / "skill/references/examples/organisation-catalogue-overlay/registry-overlay.json"
        )
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            initialise_project(
                project,
                "minimal",
                skills_root=ROOT,
                overlay_paths=(overlay,),
            )

            self.assertEqual(
                0,
                lock_main(
                    [
                        "--project-root",
                        str(project),
                        "--skills-root",
                        str(ROOT),
                        "--write",
                    ]
                ),
            )
            payload = load_lockfile(project / LOCK_PATH, ROOT)

            self.assertEqual(["org.example"], [item["source"] for item in payload["overlays"]])

    def test_profile_change_is_reviewable_composition_change(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            initialise_project(project, "minimal", skills_root=ROOT)

            assessment = assess_lock(project, ROOT, profile_name="standard")

            self.assertEqual("review-required", assessment.status)
            self.assertTrue(
                any(
                    item.component == "profile"
                    and item.status == "composition-change"
                    for item in assessment.findings
                )
            )

    def test_update_plan_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            project = workspace / "project"
            candidate = workspace / "candidate-skills"
            initialise_project(project, "minimal", skills_root=ROOT)
            shutil.copytree(
                ROOT,
                candidate,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            (candidate / "VERSION").write_text("0.9.1\n", encoding="utf-8")
            start_here = candidate / "skill/START-HERE.md"
            start_here.write_text(
                start_here.read_text(encoding="utf-8") + "\nCompatible candidate.\n",
                encoding="utf-8",
            )
            before = (project / LOCK_PATH).read_bytes()

            exit_code = lock_main(
                [
                    "--project-root",
                    str(project),
                    "--skills-root",
                    str(candidate),
                    "--plan",
                ]
            )

            self.assertEqual(0, exit_code)
            self.assertEqual(before, (project / LOCK_PATH).read_bytes())

    def test_cli_checks_and_explicitly_rewrites_lock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            initialise_project(project, "minimal", skills_root=ROOT)

            self.assertEqual(
                0,
                lock_main(
                    ["--project-root", str(project), "--skills-root", str(ROOT)]
                ),
            )
            (project / LOCK_PATH).unlink()
            self.assertEqual(
                0,
                lock_main(
                    [
                        "--project-root",
                        str(project),
                        "--skills-root",
                        str(ROOT),
                        "--write",
                    ]
                ),
            )
            self.assertTrue((project / LOCK_PATH).is_file())

    def test_lockfile_json_is_compact_and_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            initialise_project(project, "minimal", skills_root=ROOT)
            payload = json.loads((project / LOCK_PATH).read_text(encoding="utf-8"))

            first = payload["composition_digest"]
            rebuilt = build_lock_payload(project, ROOT, "minimal")

            self.assertEqual(first, rebuilt["composition_digest"])
            self.assertLess(len((project / LOCK_PATH).read_text(encoding="utf-8")), 2500)


class VersionClassificationTests(unittest.TestCase):
    def test_semantic_update_classification(self) -> None:
        self.assertEqual("current", classify_version_change("1.2.3", "1.2.3"))
        self.assertEqual("compatible-update", classify_version_change("1.2.3", "1.3.0"))
        self.assertEqual("breaking-update", classify_version_change("1.2.3", "2.0.0"))
        self.assertEqual("downgrade", classify_version_change("1.2.3", "1.1.9"))


if __name__ == "__main__":
    unittest.main()
