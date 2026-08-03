"""Release artifact and hosted-delivery contract tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from development.tools.release_preflight import _write_checksums

ROOT = Path(__file__).resolve().parents[1]


class ReleaseDeliveryTests(unittest.TestCase):
    def test_gitignore_excludes_generated_release_and_test_artifacts(self) -> None:
        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for entry in (
            "build/",
            "dist/",
            "*.egg-info/",
            ".coverage",
            "htmlcov/",
            "wheel-smoke/",
            "skill-pack-smoke/",
        ):
            self.assertIn(entry, ignored)

    def test_checksum_manifest_covers_artifacts_but_not_itself(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            dist = Path(directory)
            (dist / "get_done-1.2.3-py3-none-any.whl").write_bytes(b"wheel")
            (dist / "get_done-1.2.3.tar.gz").write_bytes(b"source")

            manifest = _write_checksums(dist, "1.2.3")

            lines = manifest.read_text(encoding="utf-8").splitlines()
            self.assertEqual(2, len(lines))
            self.assertTrue(any(line.endswith("get_done-1.2.3-py3-none-any.whl") for line in lines))
            self.assertTrue(any(line.endswith("get_done-1.2.3.tar.gz") for line in lines))
            self.assertFalse(any(manifest.name in line for line in lines))

    def test_hosted_workflows_build_and_publish_complete_artifact_sets(self) -> None:
        ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        publish = (ROOT / ".github/workflows/publish-pypi.yml").read_text(encoding="utf-8")
        for phrase in (
            "python -m build",
            "Verify isolated wheel entry points",
            "Verify standalone skill pack",
            "actions/upload-artifact@v4",
        ):
            self.assertIn(phrase, ci)
        for phrase in (
            '--tag "${GITHUB_REF_NAME}"',
            "Fetch annotated release tag",
            '"refs/tags/${GITHUB_REF_NAME}:refs/tags/${GITHUB_REF_NAME}"',
            'git cat-file -t "${GITHUB_REF_NAME}"',
            "Build skill-pack and checksums",
            "sha256sum *.whl *.tar.gz *.zip",
            "twine upload --non-interactive dist/*.whl dist/*.tar.gz",
            "gh release create",
        ):
            self.assertIn(phrase, publish)


if __name__ == "__main__":
    unittest.main()
