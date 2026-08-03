"""Build, validate, compare, and write project-local skills composition locks."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from jsonschema import Draft202012Validator

try:
    from getdone.catalogue_overlays import load_overlay
    from getdone.profiles import collect_profile_templates, load_profiles, resolve_profile
except ModuleNotFoundError as exc:  # Direct execution from the tooling directory.
    if exc.name not in {
        "getdone",
        "getdone.catalogue_overlays",
        "getdone.profiles",
    }:
        raise
    from catalogue_overlays import load_overlay
    from profiles import collect_profile_templates, load_profiles, resolve_profile

LOCK_PATH = Path(".agent/skills.lock.json")
_LOCK_VERSION = "1.0.0"
_CORE_SINGLE_FILES: tuple[Path, ...] = ()
_CORE_DIRECTORIES = (Path("skill"),)


@dataclass(frozen=True)
class LockFinding:
    component: str
    status: str
    detail: str


@dataclass(frozen=True)
class LockAssessment:
    status: str
    findings: tuple[LockFinding, ...]
    composition_digest: str
    overlay_versions: tuple[str, ...]

    @property
    def is_current(self) -> bool:
        return self.status == "current"


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return payload


def _canonical_json(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash_records(records: Iterable[tuple[str, bytes]]) -> str:
    digest = hashlib.sha256()
    for name, content in sorted(records):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(content).digest())
    return digest.hexdigest()


def _files_under(root: Path, relative: Path) -> list[Path]:
    base = root / relative
    if not base.exists():
        return []
    return sorted(path for path in base.rglob("*") if path.is_file())


def _core_records(root: Path) -> list[tuple[str, bytes]]:
    paths = [root / relative for relative in _CORE_SINGLE_FILES]
    for directory in _CORE_DIRECTORIES:
        paths.extend(_files_under(root, directory))
    excluded = {
                "skill/registry/workflows.md",
        "skill/registry/reuse-catalogue.md",
    }
    records: list[tuple[str, bytes]] = []
    for path in sorted(set(paths)):
        relative = path.relative_to(root).as_posix()
        if any(relative == prefix or relative.startswith(prefix + "/") for prefix in excluded):
            continue
        records.append((relative, path.read_bytes()))
    return records


def _profile_digest(root: Path, profile_name: str) -> tuple[dict[str, Any], str]:
    profiles = load_profiles(root)
    profile = resolve_profile(profiles, profile_name)
    templates = collect_profile_templates(root, profile, profiles=profiles)
    records = [
        (relative.as_posix(), source.read_bytes())
        for relative, source in sorted(templates.items())
    ]
    manifest = {
        "name": profile.name,
        "version": profile.version,
        "lineage": list(profile.lineage),
    }
    layer_metadata = {name: profiles[name] for name in profile.lineage}
    records.append(("profile-metadata.json", _canonical_json({
        "selected": manifest,
        "layers": layer_metadata,
    })))
    return manifest, _hash_records(records)


def _adapter_pin(root: Path) -> dict[str, str]:
    manifest_path = root / "skill/adapters/manifest.json"
    manifest = _read_json(manifest_path)
    records = [("skill/adapters/manifest.json", _canonical_json(manifest))]
    records.extend(
        (path.relative_to(root).as_posix(), path.read_bytes())
        for path in _files_under(root, Path("skill/adapters"))
        if path != manifest_path
    )
    return {
        "version": str(manifest["contract_version"]),
        "content_digest": _hash_records(records),
    }


def _safe_overlay_paths(payload: dict[str, Any], overlay_path: Path) -> list[Path]:
    paths = [overlay_path]
    for group in ("entries", "workflows"):
        for raw in payload.get(group, []):
            relative = PurePosixPath(str(raw["path"]))
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError(f"{overlay_path}: unsafe overlay document path: {relative}")
            paths.append(overlay_path.parent.joinpath(*relative.parts))
    return sorted(set(path.resolve() for path in paths))


def _portable_reference(path: Path, project_root: Path) -> str:
    path = path.resolve()
    try:
        return path.relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _overlay_pin(path: Path, project_root: Path, skills_root: Path) -> dict[str, str]:
    path = path.resolve()
    overlay = load_overlay(path, schema_root=skills_root)
    payload = _read_json(path)
    records = [
        (_portable_reference(item, path.parent), item.read_bytes())
        for item in _safe_overlay_paths(payload, path)
    ]
    return {
        "source": overlay.source,
        "version": overlay.version,
        "reference": _portable_reference(path, project_root),
        "content_digest": _hash_records(records),
    }


def _registry_versions(root: Path) -> tuple[str, str]:
    workflows = _read_json(root / "skill/registry/workflows.json")
    reuse = _read_json(root / "skill/registry/reuse-catalogue.json")
    return str(workflows["registry_version"]), str(reuse["catalogue_version"])


def _composition_digest(payload: dict[str, Any]) -> str:
    stable_overlays = [
        {
            "source": item["source"],
            "version": item["version"],
            "content_digest": item["content_digest"],
        }
        for item in payload["overlays"]
    ]
    stable = {
        "core": payload["core"],
        "profile": payload["profile"],
        "adapter_contract": payload["adapter_contract"],
        "overlays": stable_overlays,
    }
    return hashlib.sha256(_canonical_json(stable)).hexdigest()


def validate_lock_payload(payload: dict[str, Any], skills_root: Path) -> list[str]:
    schema = _read_json(skills_root / "skill/schemas/skills-lock.schema.json")
    errors = Draft202012Validator(schema).iter_errors(payload)
    messages: list[str] = []
    for error in sorted(errors, key=lambda item: tuple(str(part) for part in item.path)):
        location = ".".join(str(part) for part in error.path) or "document"
        messages.append(f"{location}: {error.message}")
    if not messages and payload["composition_digest"] != _composition_digest(payload):
        messages.append("composition_digest: does not match the locked components")
    return messages


def build_lock_payload(
    project_root: Path,
    skills_root: Path,
    profile_name: str,
    *,
    overlay_paths: Iterable[Path] = (),
    skills_reference: str | None = None,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    skills_root = skills_root.resolve()
    profile, profile_digest = _profile_digest(skills_root, profile_name)
    workflow_version, reuse_version = _registry_versions(skills_root)
    overlays = sorted(
        (_overlay_pin(path, project_root, skills_root) for path in overlay_paths),
        key=lambda item: item["source"],
    )
    if len({item["source"] for item in overlays}) != len(overlays):
        raise ValueError("composition lock cannot contain duplicate overlay sources")
    payload: dict[str, Any] = {
        "schema_version": 1,
        "lock_version": _LOCK_VERSION,
        "generated_at": date.today().isoformat(),
        "skills_reference": skills_reference or str(skills_root),
        "core": {
            "version": (skills_root / "VERSION").read_text(encoding="utf-8").strip(),
            "content_digest": _hash_records(_core_records(skills_root)),
            "workflow_registry_version": workflow_version,
            "reuse_catalogue_version": reuse_version,
        },
        "profile": {**profile, "content_digest": profile_digest},
        "adapter_contract": _adapter_pin(skills_root),
        "overlays": overlays,
    }
    payload["composition_digest"] = _composition_digest(payload)
    errors = validate_lock_payload(payload, skills_root)
    if errors:
        raise ValueError("invalid generated lock: " + "; ".join(errors))
    return payload


def load_lockfile(path: Path, skills_root: Path) -> dict[str, Any]:
    payload = _read_json(path)
    errors = validate_lock_payload(payload, skills_root)
    if errors:
        raise ValueError(f"{path}: {'; '.join(errors)}")
    return payload


def write_lockfile(
    project_root: Path,
    skills_root: Path,
    profile_name: str,
    *,
    overlay_paths: Iterable[Path] = (),
    skills_reference: str | None = None,
    overwrite: bool = False,
) -> tuple[Path, str]:
    project_root = project_root.resolve()
    destination = project_root / LOCK_PATH
    existed = destination.exists()
    if existed and not overwrite:
        return LOCK_PATH, "skipped"
    payload = build_lock_payload(
        project_root,
        skills_root,
        profile_name,
        overlay_paths=overlay_paths,
        skills_reference=skills_reference,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=destination.parent, delete=False
    ) as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, destination)
    return LOCK_PATH, "replaced" if existed else "created"


def _parse_semver(value: str) -> tuple[int, int, int] | None:
    parts = value.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        return None
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def classify_version_change(locked: str, current: str) -> str:
    if locked == current:
        return "current"
    locked_parts = _parse_semver(locked)
    current_parts = _parse_semver(current)
    if locked_parts is None or current_parts is None:
        return "unresolved"
    if current_parts < locked_parts:
        return "downgrade"
    if current_parts[0] != locked_parts[0]:
        return "breaking-update"
    return "compatible-update"


def _component_finding(
    name: str,
    locked: dict[str, Any],
    current: dict[str, Any],
) -> LockFinding:
    version_status = classify_version_change(str(locked["version"]), str(current["version"]))
    if locked["content_digest"] == current["content_digest"]:
        return LockFinding(name, "current", f"version {current['version']}")
    if version_status == "current":
        return LockFinding(name, "drift", "content changed without a version change")
    return LockFinding(name, version_status, f"{locked['version']} -> {current['version']}")


def _resolve_overlay_references(project_root: Path, locked: dict[str, Any]) -> tuple[Path, ...]:
    paths: list[Path] = []
    for overlay in locked["overlays"]:
        reference = Path(overlay["reference"])
        paths.append(reference if reference.is_absolute() else project_root / reference)
    return tuple(paths)


def locked_overlay_paths(project_root: Path, skills_root: Path) -> tuple[Path, ...]:
    locked = load_lockfile(project_root.resolve() / LOCK_PATH, skills_root.resolve())
    return _resolve_overlay_references(project_root.resolve(), locked)


def _profile_finding(locked: dict[str, Any], current: dict[str, Any]) -> LockFinding:
    if locked["name"] != current["name"] or locked["lineage"] != current["lineage"]:
        return LockFinding(
            "profile",
            "composition-change",
            f"{locked['name']} -> {current['name']}",
        )
    return _component_finding("profile", locked, current)


def _overlay_findings(locked: dict[str, Any], current: dict[str, Any]) -> list[LockFinding]:
    findings: list[LockFinding] = []
    locked_overlays = {item["source"]: item for item in locked["overlays"]}
    current_overlays = {item["source"]: item for item in current["overlays"]}
    for source in sorted(locked_overlays.keys() | current_overlays.keys()):
        if source not in current_overlays:
            findings.append(LockFinding(source, "missing", "locked overlay is unavailable"))
        elif source not in locked_overlays:
            findings.append(LockFinding(source, "added", "overlay is not in the lock"))
        else:
            findings.append(
                _component_finding(source, locked_overlays[source], current_overlays[source])
            )
    return findings


def _assessment_status(findings: list[LockFinding]) -> str:
    statuses = {finding.status for finding in findings}
    incompatible = {"drift", "breaking-update", "downgrade", "missing", "unresolved"}
    if statuses == {"current"}:
        return "current"
    if statuses & incompatible:
        return "incompatible"
    return "review-required"


def assess_lock(
    project_root: Path,
    skills_root: Path,
    *,
    overlay_paths: Iterable[Path] | None = None,
    profile_name: str | None = None,
) -> LockAssessment:
    project_root = project_root.resolve()
    skills_root = skills_root.resolve()
    locked = load_lockfile(project_root / LOCK_PATH, skills_root)
    resolved_overlays = (
        tuple(overlay_paths)
        if overlay_paths is not None
        else _resolve_overlay_references(project_root, locked)
    )
    current = build_lock_payload(
        project_root,
        skills_root,
        profile_name or str(locked["profile"]["name"]),
        overlay_paths=resolved_overlays,
        skills_reference=str(locked["skills_reference"]),
    )
    findings = [
        _component_finding("core", locked["core"], current["core"]),
        _profile_finding(locked["profile"], current["profile"]),
        _component_finding(
            "adapter_contract", locked["adapter_contract"], current["adapter_contract"]
        ),
        *_overlay_findings(locked, current),
    ]
    overlay_versions = tuple(
        f"{item['source']}@{item['version']}" for item in locked["overlays"]
    )
    return LockAssessment(
        _assessment_status(findings),
        tuple(findings),
        str(locked["composition_digest"]),
        overlay_versions,
    )
