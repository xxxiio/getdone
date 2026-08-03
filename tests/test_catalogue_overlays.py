from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "skill/references/examples/organisation-catalogue-overlay/registry-overlay.json"


class CatalogueOverlayTests(unittest.TestCase):
    def test_example_overlay_is_valid_and_searchable(self) -> None:
        from getdone.catalogue import load_catalogue, search_catalogue
        from getdone.catalogue_overlays import validate_overlay_file

        self.assertEqual([], validate_overlay_file(OVERLAY))
        catalogue = load_catalogue(ROOT, overlay_paths=(OVERLAY,))
        results = search_catalogue(catalogue, "audit event envelope", limit=5)

        self.assertGreater(len(results), 0)
        self.assertEqual("org.example.component.audit-event-envelope", results[0].entry.entry_id)
        self.assertEqual("org.example", results[0].entry.source)

    def test_overlay_namespace_is_enforced(self) -> None:
        from getdone.catalogue_overlays import validate_overlay_file

        payload = json.loads(OVERLAY.read_text(encoding="utf-8"))
        payload["entries"][0]["id"] = "org.other.component.audit-event-envelope"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "registry-overlay.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            (root / "audit-event-envelope.md").write_text(
                "# Audit Event Envelope\n",
                encoding="utf-8",
            )
            payload["entries"][0]["path"] = "audit-event-envelope.md"
            path.write_text(json.dumps(payload), encoding="utf-8")

            errors = validate_overlay_file(path)

        self.assertTrue(any("must start with org.example." in error for error in errors))


    def test_overlay_cannot_reuse_a_core_alias(self) -> None:
        from getdone.catalogue_overlays import validate_overlay_file

        payload = json.loads(OVERLAY.read_text(encoding="utf-8"))
        payload["entries"][0]["aliases"] = ["workflow.feature.test-driven-development"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            import shutil

            shutil.copytree(OVERLAY.parent, root / "overlay")
            path = root / "overlay/registry-overlay.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            errors = validate_overlay_file(path)

        self.assertTrue(any("alias must start with org.example." in error for error in errors))

    def test_search_cli_loads_overlay_and_reports_source(self) -> None:
        from getdone.search_catalogue import main

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "--repository-root",
                    str(ROOT),
                    "--overlay",
                    str(OVERLAY),
                    "--query",
                    "audit event envelope",
                    "--json",
                ]
            )

        self.assertEqual(0, exit_code)
        payload = json.loads(stdout.getvalue())
        self.assertIn("org.example", payload["sources"])
        self.assertEqual("1.0.0", payload["source_versions"]["org.example"])
        self.assertEqual("org.example", payload["results"][0]["source"])


if __name__ == "__main__":
    unittest.main()
