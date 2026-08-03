from __future__ import annotations

import contextlib
import io
import json
import unittest
from dataclasses import replace
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


class RegistryLifecycleTests(unittest.TestCase):
    def test_core_registries_use_lifecycle_schema_version_two(self) -> None:
        workflows = json.loads(
            (ROOT / "skill/registry/workflows.json").read_text(encoding="utf-8")
        )
        reuse = json.loads(
            (ROOT / "skill/registry/reuse-catalogue.json").read_text(encoding="utf-8")
        )

        self.assertEqual(2, workflows["schema_version"])
        self.assertEqual("3.0.0", workflows["registry_version"])
        self.assertEqual(2, reuse["schema_version"])
        self.assertEqual("3.0.0", reuse["catalogue_version"])

    def test_alias_resolution_returns_canonical_entry(self) -> None:
        from getdone.catalogue import Catalogue, CatalogueEntry, resolve_catalogue_entry

        entry = CatalogueEntry(
            entry_id="component.retry",
            kind="shared-component",
            title="Retry",
            status="stable",
            summary="Retry transient operations through an explicit bounded policy.",
            path=Path("skill/references/shared-components/retry.md"),
            tags=("retry",),
            languages=("any",),
            use_when=("Transient failures are expected.",),
            avoid_when=("The operation is not safe to repeat.",),
            related=(),
            aliases=("component.transient-retry",),
            introduced_in="0.6.0",
        )
        catalogue = Catalogue(version="3.0.0", entries=(entry,), workflows=())

        result = resolve_catalogue_entry(catalogue, "component.transient-retry")

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual("component.retry", result.entry.entry_id)
        self.assertEqual("component.transient-retry", result.matched_alias)

    def test_deprecated_entry_requires_active_same_kind_replacement(self) -> None:
        from getdone.catalogue import Catalogue, CatalogueEntry, validate_catalogue

        active = CatalogueEntry(
            entry_id="component.retry",
            kind="shared-component",
            title="Retry",
            status="stable",
            summary="Retry transient operations through an explicit bounded policy.",
            path=Path("skill/references/shared-components/retry.md"),
            tags=("retry",),
            languages=("any",),
            use_when=("Transient failures are expected.",),
            avoid_when=("The operation is not safe to repeat.",),
            related=(),
            introduced_in="0.6.0",
        )
        deprecated = replace(
            active,
            entry_id="component.legacy-retry",
            status="deprecated",
            path=Path("skill/references/shared-components/caching.md"),
            deprecated_in="0.7.0",
            replaced_by=None,
        )
        catalogue = Catalogue(version="3.0.0", entries=(active, deprecated), workflows=())

        errors = validate_catalogue(ROOT, catalogue)

        self.assertTrue(any("requires replaced_by" in error for error in errors))

    def test_aliases_cannot_collide_with_canonical_ids(self) -> None:
        from getdone.catalogue import Catalogue, CatalogueEntry, validate_catalogue

        first = CatalogueEntry(
            entry_id="component.retry",
            kind="shared-component",
            title="Retry",
            status="stable",
            summary="Retry transient operations through an explicit bounded policy.",
            path=Path("skill/references/shared-components/retry.md"),
            tags=("retry",),
            languages=("any",),
            use_when=("Transient failures are expected.",),
            avoid_when=("The operation is not safe to repeat.",),
            related=(),
            aliases=("component.logging",),
            introduced_in="0.6.0",
        )
        second = replace(
            first,
            entry_id="component.logging",
            title="Logging",
            path=Path("skill/references/shared-components/logging.md"),
            aliases=(),
        )
        catalogue = Catalogue(version="3.0.0", entries=(first, second), workflows=())

        errors = validate_catalogue(ROOT, catalogue)

        self.assertTrue(any("alias collides with canonical id" in error for error in errors))


    def test_retired_entry_is_hidden_from_discovery_but_exactly_resolvable(self) -> None:
        from getdone.catalogue import (
            Catalogue,
            CatalogueEntry,
            resolve_catalogue_entry,
            search_catalogue,
        )

        active = CatalogueEntry(
            entry_id="component.retry",
            kind="shared-component",
            title="Retry",
            status="stable",
            summary="Retry transient operations through an explicit bounded policy.",
            path=Path("skill/references/shared-components/retry.md"),
            tags=("retry",),
            languages=("any",),
            use_when=("Transient failures are expected.",),
            avoid_when=("The operation is not safe to repeat.",),
            related=(),
            introduced_in="0.6.0",
        )
        retired = replace(
            active,
            entry_id="component.legacy-retry",
            status="retired",
            aliases=("component.old-retry",),
            deprecated_in="0.7.0",
            replaced_by="component.retry",
        )
        catalogue = Catalogue(version="3.0.0", entries=(active, retired), workflows=())

        discovered = search_catalogue(catalogue, "legacy retry")
        resolved = resolve_catalogue_entry(catalogue, "component.old-retry")

        self.assertNotIn(
            "component.legacy-retry",
            [item.entry.entry_id for item in discovered],
        )
        self.assertIsNotNone(resolved)
        assert resolved is not None
        self.assertEqual("component.legacy-retry", resolved.entry.entry_id)
        self.assertEqual("component.retry", resolved.entry.replaced_by)

    def test_exact_id_cli_resolves_alias_and_matches_schema(self) -> None:
        from getdone.search_catalogue import main

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "--repository-root",
                    str(ROOT),
                    "--id",
                    "workflow.feature.test-driven-development",
                    "--json",
                ]
            )

        self.assertEqual(0, exit_code)
        payload = json.loads(stdout.getvalue())
        schema = json.loads(
            (ROOT / "skill/schemas/catalogue-search-result.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual([], list(Draft202012Validator(schema).iter_errors(payload)))
        self.assertEqual(3, payload["schema_version"])
        self.assertEqual("workflow.feature.tdd", payload["results"][0]["id"])
        self.assertEqual(
            "workflow.feature.test-driven-development",
            payload["results"][0]["matched_alias"],
        )


if __name__ == "__main__":
    unittest.main()
