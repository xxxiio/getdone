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


class ReuseCatalogueValidationTests(unittest.TestCase):
    def test_repository_catalogue_is_valid(self) -> None:
        from getdone.catalogue import validate_catalogue_repository

        self.assertEqual([], validate_catalogue_repository(ROOT))

    def test_core_catalogue_documents_are_inside_skill_product(self) -> None:
        from getdone.catalogue import load_catalogue

        catalogue = load_catalogue(ROOT)
        for entry in catalogue.all_entries:
            if entry.source == "core":
                self.assertTrue(entry.path.as_posix().startswith("skill/"), entry.entry_id)

    def test_repository_validation_includes_catalogue(self) -> None:
        from development.tools.validate_repository import validate_repository

        self.assertEqual([], validate_repository(ROOT))

    def test_unknown_document_path_is_rejected(self) -> None:
        from getdone.catalogue import load_catalogue, validate_catalogue

        catalogue = load_catalogue(ROOT)
        entry = catalogue.entries[0]
        invalid = entry.__class__(
            entry_id=entry.entry_id,
            kind=entry.kind,
            title=entry.title,
            status=entry.status,
            summary=entry.summary,
            path=Path("skill/references/missing.md"),
            tags=entry.tags,
            languages=entry.languages,
            use_when=entry.use_when,
            avoid_when=entry.avoid_when,
            related=entry.related,
        )
        replaced = catalogue.__class__(
            version=catalogue.version,
            entries=(invalid, *catalogue.entries[1:]),
            workflows=catalogue.workflows,
        )

        errors = validate_catalogue(ROOT, replaced)

        self.assertTrue(any("does not exist" in error for error in errors))


class ReuseCatalogueSearchTests(unittest.TestCase):
    def test_search_prefers_retry_component_for_transient_failure_query(self) -> None:
        from getdone.catalogue import load_catalogue, search_catalogue

        catalogue = load_catalogue(ROOT)
        results = search_catalogue(catalogue, "transient failure backoff", limit=5)

        self.assertGreater(len(results), 0)
        self.assertEqual("component.retry", results[0].entry.entry_id)

    def test_search_filters_kind_language_and_tag(self) -> None:
        from getdone.catalogue import load_catalogue, search_catalogue

        catalogue = load_catalogue(ROOT)
        results = search_catalogue(
            catalogue,
            "construction",
            kinds={"design-pattern"},
            languages={"python"},
            tags={"object-creation"},
        )

        self.assertGreater(len(results), 0)
        self.assertTrue(all(result.entry.kind == "design-pattern" for result in results))
        self.assertTrue(all("python" in result.entry.languages for result in results))
        self.assertTrue(all("object-creation" in result.entry.tags for result in results))

    def test_any_language_entries_match_specific_language_filter(self) -> None:
        from getdone.catalogue import load_catalogue, search_catalogue

        catalogue = load_catalogue(ROOT)
        results = search_catalogue(
            catalogue,
            "regression bug fix",
            kinds={"workflow"},
            languages={"python"},
        )

        self.assertGreater(len(results), 0)
        self.assertEqual("workflow.bug-fix.regression-first", results[0].entry.entry_id)

    def test_empty_query_lists_filtered_entries_deterministically(self) -> None:
        from getdone.catalogue import load_catalogue, search_catalogue

        catalogue = load_catalogue(ROOT)
        results = search_catalogue(catalogue, "", kinds={"shared-component"}, limit=100)
        ids = [result.entry.entry_id for result in results]

        self.assertEqual(sorted(ids), ids)
        self.assertIn("component.configuration", ids)
        self.assertIn("component.logging", ids)

    def test_cli_json_matches_published_schema(self) -> None:
        from getdone.search_catalogue import main

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "--repository-root",
                    str(ROOT),
                    "--query",
                    "state transitions",
                    "--json",
                ]
            )

        self.assertEqual(0, exit_code)
        payload = json.loads(stdout.getvalue())
        schema = json.loads(
            (ROOT / "skill/schemas/catalogue-search-result.schema.json").read_text(encoding="utf-8")
        )
        errors = list(Draft202012Validator(schema).iter_errors(payload))
        self.assertEqual([], errors)
        self.assertEqual(3, payload["schema_version"])
        self.assertEqual("3.0.0", payload["catalogue_version"])
        self.assertEqual("3.0.0", payload["workflow_registry_version"])
        self.assertEqual("3.0.0", payload["source_versions"]["core"])
        self.assertGreater(payload["count"], 0)
        self.assertEqual("pattern.state-machine", payload["results"][0]["id"])

    def test_direct_script_json_smoke(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "getdone/search_catalogue.py"),
                "--repository-root",
                str(ROOT),
                "--query",
                "transient failure backoff",
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("component.retry", payload["results"][0]["id"])

    def test_cli_rejects_unknown_kind(self) -> None:
        from getdone.search_catalogue import main

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = main(
                [
                    "--repository-root",
                    str(ROOT),
                    "--kind",
                    "unknown",
                ]
            )

        self.assertEqual(2, exit_code)
        self.assertIn("invalid choice", stderr.getvalue())


class WorkflowRegistryTests(unittest.TestCase):
    def test_workflow_registry_covers_every_canonical_workflow(self) -> None:
        from getdone.catalogue import load_catalogue

        catalogue = load_catalogue(ROOT)
        registered = {workflow.workflow_id for workflow in catalogue.workflows}
        canonical = set()
        for path in (ROOT / "skill/workflows").rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            for line in text.splitlines():
                if line.startswith("id: "):
                    canonical.add(line.removeprefix("id: ").strip())
                    break

        self.assertEqual(canonical, registered)

    def test_duplicate_entry_ids_are_rejected_by_schema(self) -> None:
        schema = json.loads(
            (ROOT / "skill/schemas/reuse-catalogue.schema.json").read_text(encoding="utf-8")
        )
        payload = json.loads(
            (ROOT / "skill/registry/reuse-catalogue.json").read_text(encoding="utf-8")
        )
        duplicate = dict(payload["entries"][0])
        payload["entries"].append(duplicate)

        # JSON Schema cannot express uniqueness by a nested property, so repository validation
        # must enforce this semantic constraint after structural validation.
        self.assertEqual([], list(Draft202012Validator(schema).iter_errors(payload)))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "skill/registry").mkdir(parents=True)
            (root / "skill/schemas").mkdir(parents=True)
            (root / "skill/registry/reuse-catalogue.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )
            (root / "skill/schemas/reuse-catalogue.schema.json").write_text(
                json.dumps(schema), encoding="utf-8"
            )
            # Semantic duplicate validation is exercised directly to keep the fixture minimal.
            from getdone.catalogue import _duplicate_entry_errors

            self.assertTrue(_duplicate_entry_errors(payload["entries"]))


if __name__ == "__main__":
    unittest.main()
