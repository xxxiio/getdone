"""Load and validate thin agent-adapter contracts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator


@dataclass(frozen=True)
class AdapterSpec:
    adapter_id: str
    display_name: str
    guidance: Path
    delivery: str
    destination: Path | None
    template: Path | None


@dataclass(frozen=True)
class AdapterContract:
    version: str
    required_guidance_references: tuple[str, ...]
    required_template_references: tuple[str, ...]
    max_guidance_nonempty_lines: int
    adapters: dict[str, AdapterSpec]


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return payload


def _validate_schema(root: Path, payload: dict[str, Any]) -> None:
    schema = _read_json(root / "skill/schemas/adapter-manifest.schema.json")
    errors = sorted(
        Draft202012Validator(schema).iter_errors(payload),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if not errors:
        return
    details = "; ".join(error.message for error in errors)
    raise ValueError(f"skill/adapters/manifest.json: {details}")


def _safe_relative_path(value: str, *, field: str, adapter_id: str) -> Path:
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError(f"adapter '{adapter_id}' has unsafe {field}: {value}")
    return Path(*pure.parts)


def load_adapter_contract(root: Path) -> AdapterContract:
    root = root.resolve()
    payload = _read_json(root / "skill/adapters/manifest.json")
    _validate_schema(root, payload)

    adapters: dict[str, AdapterSpec] = {}
    raw_adapters = payload["adapters"]
    for adapter_id, raw in raw_adapters.items():
        guidance = _safe_relative_path(raw["guidance"], field="guidance", adapter_id=adapter_id)
        destination = (
            None
            if raw["destination"] is None
            else _safe_relative_path(
                raw["destination"], field="destination", adapter_id=adapter_id
            )
        )
        template = (
            None
            if raw["template"] is None
            else _safe_relative_path(raw["template"], field="template", adapter_id=adapter_id)
        )
        adapters[adapter_id] = AdapterSpec(
            adapter_id=adapter_id,
            display_name=raw["display_name"],
            guidance=guidance,
            delivery=raw["delivery"],
            destination=destination,
            template=template,
        )

    return AdapterContract(
        version=payload["contract_version"],
        required_guidance_references=tuple(payload["required_guidance_references"]),
        required_template_references=tuple(payload["required_template_references"]),
        max_guidance_nonempty_lines=payload["max_guidance_nonempty_lines"],
        adapters=adapters,
    )


def _missing_references(text: str, required: tuple[str, ...]) -> list[str]:
    return [reference for reference in required if reference not in text]


def _validate_guidance(root: Path, contract: AdapterContract, spec: AdapterSpec) -> list[str]:
    path = root / spec.guidance
    if not path.is_file():
        return [f"{spec.guidance}: adapter guidance does not exist"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    missing = _missing_references(text, contract.required_guidance_references)
    if missing:
        errors.append(f"{spec.guidance}: missing references: {', '.join(missing)}")
    nonempty_lines = sum(bool(line.strip()) for line in text.splitlines())
    if nonempty_lines > contract.max_guidance_nonempty_lines:
        errors.append(
            f"{spec.guidance}: {nonempty_lines} non-empty lines exceeds adapter limit "
            f"of {contract.max_guidance_nonempty_lines}"
        )
    if not text.startswith("# "):
        errors.append(f"{spec.guidance}: adapter guidance must start with one H1")
    return errors


def _validate_template(root: Path, contract: AdapterContract, spec: AdapterSpec) -> list[str]:
    if spec.delivery != "project-file":
        return []
    if spec.template is None or spec.destination is None:
        return [
            "skill/adapters/manifest.json: "
            f"adapter '{spec.adapter_id}' has no project-file mapping"
        ]
    path = root / spec.template
    if not path.is_file():
        return [f"{spec.template}: adapter template does not exist"]
    text = path.read_text(encoding="utf-8")
    missing = _missing_references(text, contract.required_template_references)
    if missing:
        return [f"{spec.template}: missing references: {', '.join(missing)}"]
    return []


def validate_adapter_repository(root: Path) -> list[str]:
    root = root.resolve()
    try:
        contract = load_adapter_contract(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [str(exc)]

    errors: list[str] = []
    destinations: dict[Path, str] = {}
    for spec in contract.adapters.values():
        errors.extend(_validate_guidance(root, contract, spec))
        errors.extend(_validate_template(root, contract, spec))
        if spec.destination is None:
            continue
        previous = destinations.get(spec.destination)
        if previous is not None and previous != spec.adapter_id:
            errors.append(
                f"skill/adapters/manifest.json: adapters '{previous}' and '{spec.adapter_id}' "
                f"share destination {spec.destination}"
            )
        destinations[spec.destination] = spec.adapter_id
    return errors
