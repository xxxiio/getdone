from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from development.tools.validate_repository import (
    FORBIDDEN_LEGACY_ROOTS,
    REQUIRED_PATHS,
    validate_no_live_project_state,
    validate_product_boundary,
    validate_required_paths,
)


class ValidateRepositoryTests(unittest.TestCase):
    def test_live_project_state_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".agent" / "current").mkdir(parents=True)

            errors = validate_no_live_project_state(root)

            self.assertEqual(1, len(errors))
            self.assertIn("live project state", errors[0].message)

    def test_absent_live_state_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            errors = validate_no_live_project_state(Path(directory))
            self.assertEqual([], errors)


class FullRepositoryValidationTests(unittest.TestCase):
    def test_maintainer_infrastructure_is_consolidated_under_development(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for path in (
            Path("development/tools"),
            Path("development/scripts"),
            Path("development/benchmarks"),
            Path("development/rollout"),
        ):
            self.assertIn(path, REQUIRED_PATHS)
            self.assertTrue((root / path).is_dir())
        for path in (Path("devtools"), Path("scripts"), Path("benchmarks"), Path("rollout")):
            self.assertIn(path, FORBIDDEN_LEGACY_ROOTS)
            self.assertFalse((root / path).exists())

    def test_obsolete_maintainer_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            errors = validate_product_boundary(root)
            self.assertTrue(any(error.path == Path("scripts") for error in errors))

    def test_repository_is_valid(self) -> None:
        from development.tools.validate_repository import repository_root, validate_repository

        self.assertEqual([], validate_repository(repository_root()))


class WorkflowReferenceTests(unittest.TestCase):
    def test_repository_workflow_references_exist(self) -> None:
        from development.tools.validate_repository import repository_root, validate_workflow_references

        errors = validate_workflow_references(repository_root())
        self.assertEqual([], errors)


class ValidationCliTests(unittest.TestCase):
    def test_repository_cli_accepts_explicit_root(self) -> None:
        from development.tools.validate_repository import main

        root = Path(__file__).resolve().parents[1]
        self.assertEqual(main(["--repository-root", str(root)]), 0)

    def test_frontmatter_cli_accepts_explicit_root(self) -> None:
        from development.tools.validate_frontmatter import main

        root = Path(__file__).resolve().parents[1]
        self.assertEqual(main(["--repository-root", str(root)]), 0)


if __name__ == "__main__":
    unittest.main()
