"""Contract tests for the Typer umbrella CLI."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from typer.testing import CliRunner

from getdone.cli import app

ROOT = Path(__file__).resolve().parents[1]
RUNNER = CliRunner()


class UmbrellaCliTests(unittest.TestCase):
    def test_help_lists_mvp_commands(self) -> None:
        result = RUNNER.invoke(app, ["--help"])
        self.assertEqual(0, result.exit_code, result.stdout)
        for command in (
            "init",
            "validate",
            "guidance",
            "records",
            "status",
            "doctor",
            "planning-prompt",
        ):
            self.assertIn(command, result.stdout)
        self.assertNotIn("context", result.stdout)

    def test_version_is_eager(self) -> None:
        result = RUNNER.invoke(app, ["--version"])
        self.assertEqual(0, result.exit_code, result.stdout)
        self.assertTrue(result.stdout.strip())

    def test_planning_prompt_emits_chatgpt_file_protocol(self) -> None:
        result = RUNNER.invoke(
            app,
            ["planning-prompt", "--mode", "project", "--skills-root", str(ROOT)],
        )

        self.assertEqual(0, result.exit_code, result.output)
        self.assertIn("BEGIN GETDONE FILE", result.output)
        self.assertIn("PROJECT-PLAN", result.output)


    def test_doctor_passes_for_repository_checkout(self) -> None:
        result = RUNNER.invoke(
            app,
            ["doctor", "--project-root", str(ROOT), "--skills-root", str(ROOT)],
        )
        self.assertEqual(0, result.exit_code, result.stdout)
        self.assertIn("Skill pack", result.stdout)
        self.assertIn("pass", result.stdout)

    def test_init_and_validate_happy_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            init_result = RUNNER.invoke(
                app,
                [
                    "init",
                    "--project-root",
                    str(project),
                    "--skills-root",
                    str(ROOT),
                    "--profile",
                    "minimal",
                ],
            )
            self.assertEqual(0, init_result.exit_code, init_result.stdout)
            validate_result = RUNNER.invoke(
                app,
                [
                    "validate",
                    "--project-root",
                    str(project),
                    "--skills-root",
                    str(ROOT),
                ],
            )
            self.assertEqual(0, validate_result.exit_code, validate_result.stdout)

    def test_status_reports_authoritative_current_records_as_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            initialise_result = RUNNER.invoke(
                app,
                [
                    "init",
                    "--project-root",
                    str(project),
                    "--skills-root",
                    str(ROOT),
                    "--profile",
                    "standard",
                ],
            )
            self.assertEqual(0, initialise_result.exit_code, initialise_result.stdout)

            result = RUNNER.invoke(
                app,
                [
                    "status",
                    "--project-root",
                    str(project),
                    "--skills-root",
                    str(ROOT),
                    "--json",
                ],
            )

            self.assertEqual(0, result.exit_code, result.output)
            payload = json.loads(result.output)
            self.assertEqual("proposed", payload["current_task"]["status"])
            self.assertEqual("proposed", payload["next_step"]["status"])
            self.assertEqual([], payload["record_findings"])


if __name__ == "__main__":
    unittest.main()
