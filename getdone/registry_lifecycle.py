"""Validate stable identifiers, aliases, and replacement lifecycle metadata."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from getdone.catalogue import CatalogueEntry

SEMVER_PATTERN = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
INACTIVE_STATUSES = {"deprecated", "retired"}


def _semver(value: str) -> tuple[int, int, int] | None:
    match = SEMVER_PATTERN.fullmatch(value)
    if match is None:
        return None
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def _alias_errors(entries: tuple[CatalogueEntry, ...]) -> list[str]:
    canonical = {entry.entry_id for entry in entries}
    aliases: dict[str, str] = {}
    errors: list[str] = []
    for entry in entries:
        for alias in entry.aliases:
            if alias in canonical:
                errors.append(f"{entry.entry_id}: alias collides with canonical id: {alias}")
            previous = aliases.get(alias)
            if previous is not None:
                errors.append(f"{entry.entry_id}: alias {alias} already belongs to {previous}")
            aliases[alias] = entry.entry_id
    return errors


def _version_errors(entry: CatalogueEntry) -> list[str]:
    errors: list[str] = []
    introduced = _semver(entry.introduced_in)
    if introduced is None:
        errors.append(f"{entry.entry_id}: invalid introduced_in: {entry.introduced_in}")
    if entry.deprecated_in is None:
        return errors
    deprecated = _semver(entry.deprecated_in)
    if deprecated is None:
        errors.append(f"{entry.entry_id}: invalid deprecated_in: {entry.deprecated_in}")
    elif introduced is not None and deprecated < introduced:
        errors.append(f"{entry.entry_id}: deprecated_in precedes introduced_in")
    return errors


def _replacement_errors(
    entry: CatalogueEntry,
    by_id: dict[str, CatalogueEntry],
) -> list[str]:
    inactive = entry.status in INACTIVE_STATUSES
    if inactive and entry.replaced_by is None:
        return [f"{entry.entry_id}: {entry.status} entry requires replaced_by"]
    if inactive and entry.deprecated_in is None:
        return [f"{entry.entry_id}: {entry.status} entry requires deprecated_in"]
    if not inactive and (entry.replaced_by is not None or entry.deprecated_in is not None):
        return [f"{entry.entry_id}: active entry cannot declare deprecation metadata"]
    if entry.replaced_by is None:
        return []
    target = by_id.get(entry.replaced_by)
    if target is None:
        return [f"{entry.entry_id}: unknown replacement id: {entry.replaced_by}"]
    errors: list[str] = []
    if target.entry_id == entry.entry_id:
        errors.append(f"{entry.entry_id}: replacement cannot reference itself")
    if target.kind != entry.kind:
        errors.append(f"{entry.entry_id}: replacement must have kind {entry.kind}")
    if target.status in INACTIVE_STATUSES:
        errors.append(f"{entry.entry_id}: replacement must be active: {target.entry_id}")
    return errors


def validate_lifecycle(entries: Iterable[CatalogueEntry]) -> list[str]:
    materialised = tuple(entries)
    by_id = {entry.entry_id: entry for entry in materialised}
    errors = _alias_errors(materialised)
    for entry in materialised:
        errors.extend(_version_errors(entry))
        errors.extend(_replacement_errors(entry, by_id))
    return errors
