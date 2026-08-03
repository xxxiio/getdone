"""Load, validate, resolve, and search the machine-readable skills catalogue."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from jsonschema import Draft202012Validator

try:
    from getdone.frontmatter import parse_frontmatter
    from getdone.registry_lifecycle import validate_lifecycle
except ModuleNotFoundError as exc:  # Direct execution from the tooling directory.
    if exc.name not in {
        "getdone",
        "getdone.frontmatter",
        "getdone.registry_lifecycle",
    }:
        raise
    from frontmatter import parse_frontmatter
    from registry_lifecycle import validate_lifecycle

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
ENTRY_KINDS = (
    "workflow",
    "shared-component",
    "design-pattern",
    "decision-record",
    "worked-example",
)
ENTRY_STATUSES = ("draft", "experimental", "stable", "deprecated", "retired")
DEFAULT_SEARCH_STATUSES = {"experimental", "stable", "deprecated"}


@dataclass(frozen=True)
class CatalogueEntry:
    entry_id: str
    kind: str
    title: str
    status: str
    summary: str
    path: Path
    tags: tuple[str, ...]
    languages: tuple[str, ...]
    use_when: tuple[str, ...]
    avoid_when: tuple[str, ...]
    related: tuple[str, ...]
    aliases: tuple[str, ...] = ()
    introduced_in: str = "0.1.0"
    deprecated_in: str | None = None
    replaced_by: str | None = None
    source: str = "core"
    document_root: Path | None = None


@dataclass(frozen=True)
class WorkflowSpec:
    workflow_id: str
    title: str
    status: str
    path: Path
    summary: str
    tags: tuple[str, ...]
    languages: tuple[str, ...]
    aliases: tuple[str, ...] = ()
    introduced_in: str = "0.1.0"
    deprecated_in: str | None = None
    replaced_by: str | None = None
    source: str = "core"
    document_root: Path | None = None

    def as_entry(self) -> CatalogueEntry:
        return CatalogueEntry(
            entry_id=self.workflow_id,
            kind="workflow",
            title=self.title,
            status=self.status,
            summary=self.summary,
            path=self.path,
            tags=self.tags,
            languages=self.languages,
            use_when=("The task matches this workflow's documented purpose.",),
            avoid_when=("A more specific workflow better matches the primary task.",),
            related=(),
            aliases=self.aliases,
            introduced_in=self.introduced_in,
            deprecated_in=self.deprecated_in,
            replaced_by=self.replaced_by,
            source=self.source,
            document_root=self.document_root,
        )


@dataclass(frozen=True)
class Catalogue:
    version: str
    entries: tuple[CatalogueEntry, ...]
    workflows: tuple[WorkflowSpec, ...]
    workflow_registry_version: str = "1.0.0"
    sources: tuple[str, ...] = ("core",)
    source_versions: tuple[tuple[str, str], ...] = (("core", "1.0.0"),)

    @property
    def all_entries(self) -> tuple[CatalogueEntry, ...]:
        workflow_entries = tuple(workflow.as_entry() for workflow in self.workflows)
        return (*self.entries, *workflow_entries)


@dataclass(frozen=True)
class SearchResult:
    entry: CatalogueEntry
    score: float
    matched_alias: str | None = None


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return payload


def _schema_errors(schema: dict[str, Any], payload: dict[str, Any]) -> list[str]:
    errors = Draft202012Validator(schema).iter_errors(payload)
    messages: list[str] = []
    for error in sorted(errors, key=lambda item: tuple(str(part) for part in item.path)):
        location = ".".join(str(part) for part in error.path) or "document"
        messages.append(f"{location}: {error.message}")
    return messages


def _safe_path(value: str, *, field: str) -> Path:
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError(f"unsafe {field}: {value}")
    return Path(*pure.parts)


def _duplicate_entry_errors(entries: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for raw in entries:
        entry_id = str(raw.get("id", ""))
        if entry_id in seen:
            duplicates.append(f"duplicate catalogue id: {entry_id}")
        seen.add(entry_id)
    return duplicates


def _entry_from_raw(raw: dict[str, Any], *, source: str, document_root: Path) -> CatalogueEntry:
    return CatalogueEntry(
        entry_id=raw["id"],
        kind=raw["kind"],
        title=raw["title"],
        status=raw["status"],
        summary=raw["summary"],
        path=_safe_path(raw["path"], field="catalogue path"),
        tags=tuple(raw["tags"]),
        languages=tuple(raw["languages"]),
        use_when=tuple(raw["use_when"]),
        avoid_when=tuple(raw["avoid_when"]),
        related=tuple(raw["related"]),
        aliases=tuple(raw["aliases"]),
        introduced_in=raw["introduced_in"],
        deprecated_in=raw["deprecated_in"],
        replaced_by=raw["replaced_by"],
        source=source,
        document_root=document_root,
    )


def _workflow_from_raw(
    raw: dict[str, Any],
    *,
    source: str,
    document_root: Path,
) -> WorkflowSpec:
    return WorkflowSpec(
        workflow_id=raw["id"],
        title=raw["title"],
        status=raw["status"],
        path=_safe_path(raw["path"], field="workflow path"),
        summary=raw["summary"],
        tags=tuple(raw["tags"]),
        languages=tuple(raw["languages"]),
        aliases=tuple(raw["aliases"]),
        introduced_in=raw["introduced_in"],
        deprecated_in=raw["deprecated_in"],
        replaced_by=raw["replaced_by"],
        source=source,
        document_root=document_root,
    )


def _load_reuse_entries(root: Path) -> tuple[str, tuple[CatalogueEntry, ...]]:
    payload_path = root / "skill/registry/reuse-catalogue.json"
    schema_path = root / "skill/schemas/reuse-catalogue.schema.json"
    payload = _read_json(payload_path)
    errors = _schema_errors(_read_json(schema_path), payload)
    errors.extend(_duplicate_entry_errors(payload.get("entries", [])))
    if errors:
        raise ValueError(f"{payload_path.relative_to(root)}: {'; '.join(errors)}")
    entries = tuple(
        _entry_from_raw(raw, source="core", document_root=root) for raw in payload["entries"]
    )
    return payload["catalogue_version"], entries


def _load_workflows(root: Path) -> tuple[str, tuple[WorkflowSpec, ...]]:
    payload_path = root / "skill/registry/workflows.json"
    schema_path = root / "skill/schemas/workflow-registry.schema.json"
    payload = _read_json(payload_path)
    errors = _schema_errors(_read_json(schema_path), payload)
    errors.extend(_duplicate_entry_errors(payload.get("workflows", [])))
    if errors:
        raise ValueError(f"{payload_path.relative_to(root)}: {'; '.join(errors)}")
    workflows = tuple(
        _workflow_from_raw(raw, source="core", document_root=root)
        for raw in payload["workflows"]
    )
    return payload["registry_version"], workflows


def load_catalogue(
    root: Path,
    *,
    overlay_paths: Iterable[Path] = (),
) -> Catalogue:
    root = root.resolve()
    version, entries = _load_reuse_entries(root)
    workflow_version, workflows = _load_workflows(root)
    sources = ["core"]
    source_versions = [("core", version)]
    for overlay_path in overlay_paths:
        try:
            from getdone.catalogue_overlays import load_overlay
        except ModuleNotFoundError as exc:
            if exc.name not in {"getdone", "getdone.catalogue_overlays"}:
                raise
            from catalogue_overlays import load_overlay
        overlay = load_overlay(overlay_path.resolve(), schema_root=root)
        entries = (*entries, *overlay.entries)
        workflows = (*workflows, *overlay.workflows)
        sources.append(overlay.source)
        source_versions.append((overlay.source, overlay.version))
    return Catalogue(
        version=version,
        entries=entries,
        workflows=workflows,
        workflow_registry_version=workflow_version,
        sources=tuple(sources),
        source_versions=tuple(source_versions),
    )


def _first_heading(path: Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return None


def _document_path(root: Path, entry: CatalogueEntry) -> Path:
    return (entry.document_root or root) / entry.path


def _validate_paths_and_headings(root: Path, entries: Iterable[CatalogueEntry]) -> list[str]:
    errors: list[str] = []
    for entry in entries:
        if entry.source == "core" and not entry.path.as_posix().startswith("skill/"):
            errors.append(f"{entry.entry_id}: core document is outside skill/: {entry.path}")
        path = _document_path(root, entry)
        if not path.is_file():
            errors.append(f"{entry.entry_id}: document does not exist: {entry.path}")
            continue
        if _first_heading(path) is None:
            errors.append(f"{entry.entry_id}: document has no H1 heading: {entry.path}")
    return errors


def _canonical_core_workflows(root: Path) -> dict[str, Path]:
    workflows: dict[str, Path] = {}
    for path in sorted((root / "skill/workflows").rglob("*.md")):
        document = parse_frontmatter(path.read_text(encoding="utf-8"))
        workflows[str(document.data.get("id", ""))] = path.relative_to(root)
    return workflows


def _validate_workflow_coverage(root: Path, workflows: tuple[WorkflowSpec, ...]) -> list[str]:
    canonical = _canonical_core_workflows(root)
    registered = {item.workflow_id: item for item in workflows if item.source == "core"}
    errors: list[str] = []
    for missing in sorted(set(canonical) - set(registered)):
        errors.append(f"skill/registry/workflows.json: missing workflow: {missing}")
    for extra in sorted(set(registered) - set(canonical)):
        errors.append(f"skill/registry/workflows.json: unknown workflow: {extra}")
    return errors


def _validate_workflow_documents(root: Path, workflows: tuple[WorkflowSpec, ...]) -> list[str]:
    errors: list[str] = []
    for workflow in workflows:
        entry = workflow.as_entry()
        path = _document_path(root, entry)
        if not path.is_file():
            continue
        document = parse_frontmatter(path.read_text(encoding="utf-8"))
        canonical_id = str(document.data.get("id", ""))
        canonical_status = str(document.data.get("status", ""))
        heading = _first_heading(path)
        if canonical_id != workflow.workflow_id:
            errors.append(f"{workflow.workflow_id}: document id is {canonical_id!r}")
        if canonical_status != workflow.status:
            errors.append(f"{workflow.workflow_id}: document status is {canonical_status!r}")
        if heading is not None and heading != workflow.title:
            errors.append(
                f"{workflow.workflow_id}: registry title {workflow.title!r} "
                f"does not match H1 {heading!r}"
            )
    return errors


def _validate_related(entries: tuple[CatalogueEntry, ...]) -> list[str]:
    known = {entry.entry_id for entry in entries}
    errors: list[str] = []
    for entry in entries:
        for related_id in entry.related:
            if related_id not in known:
                errors.append(f"{entry.entry_id}: unknown related id: {related_id}")
    return errors


def validate_catalogue(root: Path, catalogue: Catalogue) -> list[str]:
    root = root.resolve()
    entries = catalogue.all_entries
    errors = _validate_paths_and_headings(root, entries)
    errors.extend(_validate_related(entries))
    errors.extend(_validate_workflow_coverage(root, catalogue.workflows))
    errors.extend(_validate_workflow_documents(root, catalogue.workflows))
    errors.extend(validate_lifecycle(entries))
    ids = [entry.entry_id for entry in entries]
    for entry_id in sorted({value for value in ids if ids.count(value) > 1}):
        errors.append(f"duplicate id across registries: {entry_id}")
    return errors


def validate_catalogue_repository(root: Path) -> list[str]:
    try:
        catalogue = load_catalogue(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [str(exc)]
    return validate_catalogue(root, catalogue)


def resolve_catalogue_entry(catalogue: Catalogue, entry_id: str) -> SearchResult | None:
    for entry in catalogue.all_entries:
        if entry.entry_id == entry_id:
            return SearchResult(entry=entry, score=1000.0)
        if entry_id in entry.aliases:
            return SearchResult(entry=entry, score=1000.0, matched_alias=entry_id)
    return None


def _tokens(value: str) -> tuple[str, ...]:
    return tuple(TOKEN_PATTERN.findall(value.lower()))


def _contains_all(required: set[str] | None, values: tuple[str, ...]) -> bool:
    if required is None or "any" in values:
        return True
    return required.issubset(set(values))


def _score(entry: CatalogueEntry, query_tokens: tuple[str, ...]) -> float:
    if not query_tokens:
        return 0.0
    fields = (
        (entry.entry_id, 7.0),
        (" ".join(entry.aliases), 7.0),
        (entry.title, 6.0),
        (" ".join(entry.tags), 5.0),
        (entry.summary, 3.0),
        (" ".join(entry.use_when), 2.0),
        (" ".join(entry.avoid_when), 1.0),
    )
    score = 0.0
    for token in query_tokens:
        for text, weight in fields:
            words = _tokens(text)
            if token in words:
                score += weight
            elif any(word.startswith(token) or token.startswith(word) for word in words):
                score += weight * 0.5
    if entry.status == "deprecated":
        score *= 0.5
    return score


def search_catalogue(
    catalogue: Catalogue,
    query: str,
    *,
    kinds: set[str] | None = None,
    languages: set[str] | None = None,
    tags: set[str] | None = None,
    statuses: set[str] | None = None,
    limit: int = 20,
) -> tuple[SearchResult, ...]:
    query_tokens = _tokens(query)
    effective_statuses = DEFAULT_SEARCH_STATUSES if statuses is None else statuses
    results: list[SearchResult] = []
    for entry in catalogue.all_entries:
        if kinds is not None and entry.kind not in kinds:
            continue
        if entry.status not in effective_statuses:
            continue
        if not _contains_all(languages, entry.languages):
            continue
        if not _contains_all(tags, entry.tags):
            continue
        score = _score(entry, query_tokens)
        if query_tokens and score == 0:
            continue
        results.append(SearchResult(entry=entry, score=score))
    results.sort(key=lambda result: (-result.score, result.entry.entry_id))
    return tuple(results[:limit])
