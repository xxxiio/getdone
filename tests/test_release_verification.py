from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from development.tools.verify_release import verify_release_metadata

ROOT = Path(__file__).resolve().parents[1]


class ReleaseMetadataTests(unittest.TestCase):
    def test_repository_release_metadata_agrees(self) -> None:
        report = verify_release_metadata(ROOT)
        self.assertTrue(report.is_valid)
        self.assertEqual((), report.errors)

    @staticmethod
    def _dynamic_pyproject() -> str:
        return (
            '[project]\nname = "example"\ndynamic = ["version"]\n\n'
            '[tool.setuptools.dynamic]\nversion = {file = ["VERSION"]}\n'
        )

    def test_duplicate_literal_version_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "VERSION").write_text("1.2.3\n", encoding="utf-8")
            (root / "pyproject.toml").write_text(
                '[project]\nname = "example"\nversion = "1.2.4"\n',
                encoding="utf-8",
            )
            (root / "CHANGELOG.md").write_text(
                "# Changelog\n\n## 1.2.3 - 2026-07-26\n",
                encoding="utf-8",
            )

            report = verify_release_metadata(root)

            self.assertFalse(report.is_valid)
            self.assertTrue(any("duplicate literal" in error for error in report.errors))

    def test_wrong_dynamic_version_source_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "VERSION").write_text("1.2.3\n", encoding="utf-8")
            (root / "pyproject.toml").write_text(
                '[project]\nname = "example"\ndynamic = ["version"]\n\n'
                '[tool.setuptools.dynamic]\nversion = {file = ["VERSION.txt"]}\n',
                encoding="utf-8",
            )
            (root / "CHANGELOG.md").write_text(
                "# Changelog\n\n## 1.2.3 - 2026-07-26\n", encoding="utf-8"
            )

            report = verify_release_metadata(root)

            self.assertFalse(report.is_valid)
            self.assertTrue(any("derive" in error for error in report.errors))

    def test_missing_changelog_entry_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "VERSION").write_text("1.2.3\n", encoding="utf-8")
            (root / "pyproject.toml").write_text(self._dynamic_pyproject(), encoding="utf-8")
            (root / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")

            report = verify_release_metadata(root)

            self.assertFalse(report.is_valid)
            self.assertTrue(any("changelog" in error for error in report.errors))

    def test_annotated_unsigned_tag_is_warning_unless_signature_required(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "VERSION").write_text("1.2.3\n", encoding="utf-8")
            (root / "pyproject.toml").write_text(self._dynamic_pyproject(), encoding="utf-8")
            (root / "CHANGELOG.md").write_text(
                "# Changelog\n\n## 1.2.3 - 2026-07-26\n",
                encoding="utf-8",
            )
            for args in (
                ("init",),
                ("config", "user.name", "Test"),
                ("config", "user.email", "test@example.invalid"),
                ("add", "."),
                ("commit", "-m", "release"),
                ("tag", "-a", "v1.2.3", "-m", "release 1.2.3"),
            ):
                subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

            unsigned = verify_release_metadata(root, tag="v1.2.3")
            required = verify_release_metadata(
                root, tag="v1.2.3", require_signature=True
            )

            self.assertTrue(unsigned.is_valid)
            self.assertTrue(any("not signature-verified" in item for item in unsigned.warnings))
            self.assertFalse(required.is_valid)
            self.assertTrue(any("signature verification failed" in item for item in required.errors))


if __name__ == "__main__":
    unittest.main()
