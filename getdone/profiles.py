"""Bootstrap profile loading, inheritance resolution, and template overlays."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


ProfilePayload = Mapping[str, Any]


@dataclass(frozen=True)
class ResolvedProfile:
    """A profile with its parent-first inheritance lineage."""

    name: str
    version: str
    description: str
    lineage: tuple[str, ...]


def load_profiles(root: Path) -> dict[str, dict[str, Any]]:
    """Load raw profile definitions from the repository manifest."""

    manifest_path = root / "skill/bootstrap/manifests.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    profiles = payload.get("profiles")
    if not isinstance(profiles, dict):
        raise ValueError("invalid bootstrap manifest: 'profiles' must be an object")

    normalised: dict[str, dict[str, Any]] = {}
    for name, profile in profiles.items():
        if not isinstance(name, str) or not isinstance(profile, dict):
            raise ValueError("invalid bootstrap manifest: profile entries must be objects")
        normalised[name] = profile
    return normalised


def _parents(profile_name: str, payload: ProfilePayload) -> tuple[str, ...]:
    raw = payload.get("extends", [])
    if raw is None:
        return ()
    if not isinstance(raw, list) or not all(isinstance(item, str) and item for item in raw):
        raise ValueError(f"profile '{profile_name}' extends must be an array of profile names")
    return tuple(raw)


def resolve_profile(
    profiles: Mapping[str, ProfilePayload],
    profile_name: str,
) -> ResolvedProfile:
    """Resolve a profile to a deterministic parent-first lineage."""

    if profile_name not in profiles:
        valid = ", ".join(sorted(profiles))
        raise ValueError(f"unknown bootstrap profile '{profile_name}'. Valid profiles: {valid}")

    lineage: list[str] = []
    resolved: set[str] = set()
    active: list[str] = []

    def visit(name: str) -> None:
        if name in resolved:
            return
        if name in active:
            cycle = " -> ".join((*active[active.index(name) :], name))
            raise ValueError(f"bootstrap profile inheritance cycle: {cycle}")
        payload = profiles.get(name)
        if payload is None:
            parent = active[-1] if active else profile_name
            raise ValueError(f"profile '{parent}' extends unknown profile '{name}'")

        active.append(name)
        for parent in _parents(name, payload):
            visit(parent)
        active.pop()
        resolved.add(name)
        lineage.append(name)

    visit(profile_name)
    selected = profiles[profile_name]
    version = selected.get("version")
    description = selected.get("description")
    if not isinstance(version, str) or not version:
        raise ValueError(f"profile '{profile_name}' has no version")
    if not isinstance(description, str) or not description:
        raise ValueError(f"profile '{profile_name}' has no description")
    return ResolvedProfile(profile_name, version, description, tuple(lineage))


def collect_profile_templates(
    root: Path,
    profile: ResolvedProfile,
    *,
    profiles: Mapping[str, ProfilePayload] | None = None,
) -> dict[Path, Path]:
    """Collect inherited profile files with child layers overriding parents."""

    profiles = profiles or load_profiles(root)
    templates: dict[Path, Path] = {}
    for layer_name in profile.lineage:
        payload = profiles[layer_name]
        source = payload.get("source")
        if source is None:
            continue
        if not isinstance(source, str) or not source:
            raise ValueError(f"profile '{layer_name}' source must be a non-empty path")
        source_root = root / source
        if not source_root.is_dir():
            raise FileNotFoundError(
                f"bootstrap profile directory does not exist for '{layer_name}': {source_root}"
            )
        for source_path in sorted(path for path in source_root.rglob("*") if path.is_file()):
            templates[source_path.relative_to(source_root)] = source_path
    return templates
