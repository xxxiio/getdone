"""Validate the frozen v1 public contract manifest."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _schema_version(schema: dict[str, Any]) -> int | None:
    value = schema.get("properties", {}).get("schema_version", {}).get("const")
    return value if isinstance(value, int) else None


def _metadata(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    profiles = _load_json(root / "skill/bootstrap/manifests.json")
    adapters = _load_json(root / "skill/adapters/manifest.json")
    return pyproject, profiles, adapters


def validate_public_contracts(root: Path) -> list[str]:
    root = root.resolve()
    manifest = _load_json(root / "skill/contracts/public-contracts.json")
    schema = _load_json(root / "skill/schemas/public-contracts.schema.json")
    errors = [error.message for error in Draft202012Validator(schema).iter_errors(manifest)]
    pyproject, profiles, adapters = _metadata(root)
    scripts = set(pyproject.get("project", {}).get("scripts", {}))
    expected_scripts = set(manifest.get("cli_commands", []))
    if scripts != expected_scripts:
        errors.append("CLI command set differs from the frozen public contract")
    actual_profiles = {
        name: item.get("version") for name, item in profiles.get("profiles", {}).items()
    }
    if actual_profiles != manifest.get("bootstrap_profiles"):
        errors.append("bootstrap profile versions differ from the frozen public contract")
    if adapters.get("contract_version") != manifest.get("adapter_contract_version"):
        errors.append("adapter contract version differs from the frozen public contract")
    for name, item in manifest.get("schemas", {}).items():
        path = root / item["path"]
        if not path.is_file():
            errors.append(f"{name}: schema path does not exist: {item['path']}")
        elif _schema_version(_load_json(path)) != item["version"]:
            errors.append(f"{name}: schema version differs from the frozen contract")
    return errors
