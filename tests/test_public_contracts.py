from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from development.tools.public_contracts import validate_public_contracts

ROOT = Path(__file__).resolve().parents[1]


class PublicContractTests(unittest.TestCase):
    def test_repository_matches_frozen_contract(self) -> None:
        self.assertEqual([], validate_public_contracts(ROOT))

    def test_cli_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in (
                "skill/contracts/public-contracts.json",
                "skill/schemas/public-contracts.schema.json",
                "skill/bootstrap/manifests.json",
                "skill/adapters/manifest.json",
                "pyproject.toml",
            ):
                source = ROOT / relative
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
            for item in json.loads(
                (ROOT / "skill/contracts/public-contracts.json").read_text(encoding="utf-8")
            )["schemas"].values():
                source = ROOT / item["path"]
                target = root / item["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
            contract_path = root / "skill/contracts/public-contracts.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["cli_commands"].remove("getdone-init")
            contract_path.write_text(json.dumps(contract), encoding="utf-8")

            errors = validate_public_contracts(root)

            self.assertTrue(any("CLI command set" in error for error in errors))

    def test_pre_release_surface_has_no_legacy_compatibility_layer(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        contract = json.loads(
            (ROOT / "skill/contracts/public-contracts.json").read_text(encoding="utf-8")
        )
        schema = json.loads(
            (ROOT / "skill/schemas/public-contracts.schema.json").read_text(encoding="utf-8")
        )

        self.assertNotIn("agent-skills-", pyproject)
        self.assertNotIn("tooling*", pyproject)
        self.assertNotIn("deprecated_cli_aliases", contract)
        self.assertNotIn("deprecated_cli_aliases", schema["properties"])
        self.assertFalse((ROOT / "tooling").exists())


if __name__ == "__main__":
    unittest.main()
