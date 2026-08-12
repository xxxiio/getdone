from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


class ContextSelectionTests(unittest.TestCase):
    def test_feature_selection_includes_required_contracts_only(self) -> None:
        from getdone.context_selection import select_context

        selection = select_context(ROOT, "feature", "python")

        self.assertEqual(
            "skill/workflows/feature/tdd-feature-development.md",
            selection.workflow,
        )
        self.assertIn("skill/workflows/general/deterministic-development.md", selection.documents)
        self.assertIn("skill/acceptance/change-types/feature.md", selection.documents)
        self.assertIn("skill/standards/languages/python.md", selection.documents)
        self.assertIn("skill/standards/core.md", selection.documents)
        self.assertNotIn("skill/standards/languages/rust.md", selection.documents)
        self.assertNotIn("skill/acceptance/change-types/database-change.md", selection.documents)

    def test_supported_task_classes_route_deterministically(self) -> None:
        from getdone.context_selection import select_context

        expected = {
            "feature": "skill/workflows/feature/tdd-feature-development.md",
            "bug-fix": "skill/workflows/bug-fix/regression-first-bug-fix.md",
            "refactoring": "skill/workflows/refactoring/characterisation-first-refactoring.md",
            "investigation": "skill/workflows/general/technical-investigation.md",
            "project-planning": "skill/workflows/general/project-planning.md",
            "execution-planning": "skill/workflows/general/execution-planning.md",
        }

        for task_class, workflow in expected.items():
            with self.subTest(task_class=task_class):
                self.assertEqual(workflow, select_context(ROOT, task_class, "rust").workflow)

    def test_polyglot_selection_includes_each_affected_language_once(self) -> None:
        from getdone.context_selection import select_context

        selection = select_context(ROOT, "feature", ["python", "rust", "python", "q-kdbplus"])

        self.assertEqual(("python", "rust", "q-kdbplus"), selection.languages)
        self.assertIn("skill/standards/languages/python.md", selection.documents)
        self.assertIn("skill/standards/languages/rust.md", selection.documents)
        self.assertIn("skill/standards/languages/q-kdbplus.md", selection.documents)
        self.assertEqual(1, selection.documents.count("skill/standards/languages/python.md"))

    def test_planning_selection_uses_record_contract_without_language_standard(self) -> None:
        from getdone.context_selection import select_context

        selection = select_context(ROOT, "project-planning", "python")

        self.assertIn("skill/contracts/project-records.md", selection.documents)
        self.assertIn("skill/acceptance/change-types/project-planning.md", selection.documents)
        self.assertNotIn("skill/standards/languages/python.md", selection.documents)
        self.assertLessEqual(len(selection.documents), 5)

    def test_manifest_matches_schema(self) -> None:
        from getdone.context_selection import select_context

        payload = select_context(ROOT, "bug-fix", "cpp").to_dict()
        schema = json.loads(
            (ROOT / "skill/schemas/context-selection-manifest.schema.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual([], list(Draft202012Validator(schema).iter_errors(payload)))

    def test_selection_is_compact_and_deterministic(self) -> None:
        from getdone.context_selection import select_context

        first = select_context(ROOT, "refactoring", "dart-flutter")
        second = select_context(ROOT, "refactoring", "dart-flutter")

        self.assertEqual(first.selection_digest, second.selection_digest)
        self.assertLess(first.approximate_tokens, 7000)
        self.assertLess(len(first.documents), 24)

    def test_cli_json_smoke(self) -> None:
        from getdone.context_selection import main

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "--repository-root",
                    str(ROOT),
                    "--task-class",
                    "feature",
                    "--language",
                    "python",
                    "--language",
                    "rust",
                    "--json",
                ]
            )

        self.assertEqual(0, exit_code)
        payload = json.loads(stdout.getvalue())
        self.assertEqual("feature", payload["task_class"])
        self.assertEqual("python", payload["primary_language"])
        self.assertEqual(["python", "rust"], payload["languages"])

    def test_direct_script_smoke(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "getdone/context_selection.py"),
                "--repository-root",
                str(ROOT),
                "--task-class",
                "investigation",
                "--language",
                "q-kdbplus",
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("q-kdbplus", payload["primary_language"])
        self.assertEqual(["q-kdbplus"], payload["languages"])


class ContextSelectionBenchmarkTests(unittest.TestCase):
    def test_published_report_path_uses_repository_version(self) -> None:
        from development.tools.benchmark_context_selection import _published_report_path

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "VERSION").write_text("9.8.7\n", encoding="utf-8")

            self.assertEqual(
                root / "development/benchmarks/context-selection/results/9.8.7.json",
                _published_report_path(root),
            )

    def test_published_report_matches_current_repository(self) -> None:
        from development.tools.benchmark_context_selection import validate_published_report

        self.assertEqual([], validate_published_report(ROOT))

    def test_representative_benchmark_meets_evidence_gate(self) -> None:
        from development.tools.benchmark_context_selection import run_benchmark

        report = run_benchmark(ROOT)

        self.assertEqual(1.0, report["route_accuracy"])
        self.assertEqual(1.0, report["required_document_recall"])
        self.assertEqual(0, report["missed_acceptance_gates"])
        self.assertGreaterEqual(report["average_token_reduction"], 0.65)
        self.assertTrue(report["tooling_justified"])


if __name__ == "__main__":
    unittest.main()
