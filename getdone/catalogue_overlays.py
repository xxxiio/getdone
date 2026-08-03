"""Load and validate organisation-owned catalogue overlays."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

try:
    from getdone.catalogue import (
        CatalogueEntry,
        WorkflowSpec,
        _entry_from_raw,
        _read_json,
        _workflow_from_raw,
    )
except ModuleNotFoundError as exc:  # Direct execution from the tooling directory.
    if exc.name not in {"getdone", "getdone.catalogue"}:
        raise
    from catalogue import (  # type: ignore[no-redef]
        CatalogueEntry,
        WorkflowSpec,
        _entry_from_raw,
        _read_json,
        _workflow_from_raw,
    )


@dataclass(frozen=True)
class CatalogueOverlay:
    source: str
    version: str
    entries: tuple[CatalogueEntry, ...]
    workflows: tuple[WorkflowSpec, ...]


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _schema_errors(schema: dict[str, Any], payload: dict[str, Any]) -> list[str]:
    messages: list[str] = []
    for error in Draft202012Validator(schema).iter_errors(payload):
        location = ".".join(str(part) for part in error.path) or "document"
        messages.append(f"{location}: {error.message}")
    return sorted(messages)


def _namespace_errors(payload: dict[str, Any]) -> list[str]:
    namespace = str(payload.get("namespace", ""))
    entry_prefix = f"org.{namespace}."
    workflow_prefix = f"workflow.org.{namespace}."
    errors: list[str] = []
    for raw in payload.get("entries", []):
        entry_id = str(raw.get("id", ""))
        if not entry_id.startswith(entry_prefix):
            errors.append(f"{entry_id}: overlay entry id must start with {entry_prefix}")
        for alias in raw.get("aliases", []):
            if not str(alias).startswith(entry_prefix):
                errors.append(f"{entry_id}: alias must start with {entry_prefix}: {alias}")
    for raw in payload.get("workflows", []):
        workflow_id = str(raw.get("id", ""))
        if not workflow_id.startswith(workflow_prefix):
            errors.append(
                f"{workflow_id}: overlay workflow id must start with {workflow_prefix}"
            )
    return errors


def _duplicate_errors(payload: dict[str, Any]) -> list[str]:
    ids = [str(raw.get("id", "")) for key in ("entries", "workflows") for raw in payload[key]]
    return [f"duplicate overlay id: {value}" for value in sorted(set(ids)) if ids.count(value) > 1]


def load_overlay(path: Path, *, schema_root: Path | None = None) -> CatalogueOverlay:
    path = path.resolve()
    schema_base = (schema_root or repository_root()).resolve()
    payload = _read_json(path)
    schema = _read_json(schema_base / "skill/schemas/catalogue-overlay.schema.json")
    errors = _schema_errors(schema, payload)
    errors.extend(_namespace_errors(payload))
    errors.extend(_duplicate_errors(payload))
    if errors:
        raise ValueError(f"{path}: {'; '.join(errors)}")
    source = f"org.{payload['namespace']}"
    document_root = path.parent
    entries = tuple(
        _entry_from_raw(raw, source=source, document_root=document_root)
        for raw in payload["entries"]
    )
    workflows = tuple(
        _workflow_from_raw(raw, source=source, document_root=document_root)
        for raw in payload["workflows"]
    )
    return CatalogueOverlay(
        source=source,
        version=payload["overlay_version"],
        entries=entries,
        workflows=workflows,
    )


def validate_overlay_file(path: Path, *, schema_root: Path | None = None) -> list[str]:
    root = (schema_root or repository_root()).resolve()
    try:
        from getdone.catalogue import load_catalogue, validate_catalogue
    except ModuleNotFoundError as exc:
        if exc.name not in {"getdone", "getdone.catalogue"}:
            raise
        from catalogue import load_catalogue, validate_catalogue
    try:
        catalogue = load_catalogue(root, overlay_paths=(path,))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [str(exc)]
    return validate_catalogue(root, catalogue)
