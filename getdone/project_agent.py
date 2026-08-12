"""Project-specific agent extension discovery, validation, and bounded selection."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, NotRequired, TypedDict, cast

PROJECT_AGENT_DIR = ".project-agent"
BASELINE_FILE = "AGENTS.md"
INDEX_FILE = "index.json"
BASELINE_TOKEN_WARNING = 2000
SELECTED_TOKEN_WARNING = 6000

SUPPORTED_LANGUAGES = (
    "python",
    "q-kdbplus",
    "cpp",
    "rust",
    "dart-flutter",
    "typescript",
)

DEFAULT_LANGUAGE_PATTERNS: dict[str, tuple[str, ...]] = {
    "python": ("**/*.py",),
    "q-kdbplus": ("**/*.q", "**/*.k"),
    "cpp": (
        "**/*.c",
        "**/*.cc",
        "**/*.cpp",
        "**/*.cxx",
        "**/*.h",
        "**/*.hh",
        "**/*.hpp",
        "**/*.hxx",
    ),
    "rust": ("**/*.rs",),
    "dart-flutter": ("**/*.dart",),
    "typescript": ("**/*.ts", "**/*.tsx"),
}


class ProjectAgentError(ValueError):
    """Raised when a project-agent extension cannot be selected safely."""


@dataclass(frozen=True)
class ProjectAgentFinding:
    severity: str
    path: str
    message: str


@dataclass(frozen=True)
class ProjectAgentHealth:
    exists: bool
    root: str
    baseline_tokens: int | None
    rule_count: int
    inference_count: int
    referenced_files: int
    errors: tuple[ProjectAgentFinding, ...]
    warnings: tuple[ProjectAgentFinding, ...]

    @property
    def is_valid(self) -> bool:
        return self.exists and not self.errors


@dataclass(frozen=True)
class ProjectAgentSelection:
    documents: tuple[str, ...]
    matched_rules: tuple[str, ...]
    explicit_concerns: tuple[str, ...]
    inferred_concerns: tuple[str, ...]
    concerns: tuple[str, ...]
    affected_languages: tuple[str, ...]
    approximate_tokens: int
    selection_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "documents": list(self.documents),
            "matched_rules": list(self.matched_rules),
            "explicit_concerns": list(self.explicit_concerns),
            "inferred_concerns": list(self.inferred_concerns),
            "concerns": list(self.concerns),
            "affected_languages": list(self.affected_languages),
            "approximate_tokens": self.approximate_tokens,
            "selection_digest": self.selection_digest,
        }


def project_agent_root(project_root: Path) -> Path:
    return project_root.resolve() / PROJECT_AGENT_DIR


def discover_project_agent(project_root: Path) -> Path | None:
    root = project_agent_root(project_root)
    return root if root.is_dir() else None


def _normalise(path: str) -> str:
    return path.replace("\\", "/").removeprefix("./")


def _matches(path: str, patterns: Iterable[str]) -> bool:
    normalised = _normalise(path)
    return any(fnmatch.fnmatch(normalised, pattern) for pattern in patterns)


def _deduplicate(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _tokens(path: Path) -> int:
    return max(1, math.ceil(len(path.read_text(encoding="utf-8")) / 4))


class _InferenceRule(TypedDict):
    paths: list[str]
    concerns: list[str]


class _SelectionRule(TypedDict):
    id: str
    load: list[str]
    paths: NotRequired[list[str]]
    concerns: NotRequired[list[str]]


class _ProjectAgentIndex(TypedDict):
    schema_version: int
    language_patterns: NotRequired[dict[str, list[str]]]
    infer: NotRequired[list[_InferenceRule]]
    rules: list[_SelectionRule]


def _string_list(value: object, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list):
        raise ProjectAgentError(f"{label} must be a string list")
    items = cast(list[object], value)
    if not allow_empty and not items:
        raise ProjectAgentError(f"{label} must be a non-empty string list")
    if not all(isinstance(item, str) and item for item in items):
        qualifier = "a string list" if allow_empty else "a non-empty string list"
        raise ProjectAgentError(f"{label} must be {qualifier}")
    return cast(list[str], items)


def _parse_index(payload: object) -> _ProjectAgentIndex:
    if not isinstance(payload, dict):
        raise ProjectAgentError("project-agent index must be a JSON object")
    raw = cast(dict[object, object], payload)

    if raw.get("schema_version") != 1:
        raise ProjectAgentError("project-agent index schema_version must be 1")

    language_patterns_value = raw.get("language_patterns", {})
    if not isinstance(language_patterns_value, dict):
        raise ProjectAgentError("language_patterns must be an object")
    language_patterns_raw = cast(dict[object, object], language_patterns_value)
    language_patterns: dict[str, list[str]] = {}
    for language_value, patterns_value in language_patterns_raw.items():
        if not isinstance(language_value, str):
            raise ProjectAgentError("language_patterns keys must be strings")
        if language_value not in SUPPORTED_LANGUAGES:
            raise ProjectAgentError(
                f"unsupported project-agent language: {language_value}"
            )
        language_patterns[language_value] = _string_list(
            patterns_value,
            f"language_patterns.{language_value}",
        )

    infer_value = raw.get("infer", [])
    if not isinstance(infer_value, list):
        raise ProjectAgentError("infer must be a list")
    infer: list[_InferenceRule] = []
    for position, rule_value in enumerate(cast(list[object], infer_value)):
        if not isinstance(rule_value, dict):
            raise ProjectAgentError(f"infer[{position}] must be an object")
        rule_raw = cast(dict[object, object], rule_value)
        infer.append(
            {
                "paths": _string_list(
                    rule_raw.get("paths"),
                    f"infer[{position}].paths",
                ),
                "concerns": _string_list(
                    rule_raw.get("concerns"),
                    f"infer[{position}].concerns",
                ),
            }
        )

    rules_value = raw.get("rules", [])
    if not isinstance(rules_value, list):
        raise ProjectAgentError("rules must be a list")
    rules: list[_SelectionRule] = []
    seen: set[str] = set()
    for position, rule_value in enumerate(cast(list[object], rules_value)):
        if not isinstance(rule_value, dict):
            raise ProjectAgentError(f"rules[{position}] must be an object")
        rule_raw = cast(dict[object, object], rule_value)

        rule_id_value = rule_raw.get("id")
        if not isinstance(rule_id_value, str) or not rule_id_value:
            raise ProjectAgentError(
                f"rules[{position}].id must be a non-empty string"
            )
        if rule_id_value in seen:
            raise ProjectAgentError(
                f"duplicate project-agent rule id: {rule_id_value}"
            )
        seen.add(rule_id_value)

        paths = _string_list(
            rule_raw.get("paths", []),
            f"rule {rule_id_value}: paths",
            allow_empty=True,
        )
        concerns = _string_list(
            rule_raw.get("concerns", []),
            f"rule {rule_id_value}: concerns",
            allow_empty=True,
        )
        if not paths and not concerns:
            raise ProjectAgentError(
                f"rule {rule_id_value}: at least one paths or concerns selector is required"
            )
        load = _string_list(
            rule_raw.get("load"),
            f"rule {rule_id_value}: load",
        )

        rule: _SelectionRule = {"id": rule_id_value, "load": load}
        if paths:
            rule["paths"] = paths
        if concerns:
            rule["concerns"] = concerns
        rules.append(rule)

    return {
        "schema_version": 1,
        "language_patterns": language_patterns,
        "infer": infer,
        "rules": rules,
    }


def _read_index(root: Path) -> _ProjectAgentIndex:
    path = root / INDEX_FILE
    try:
        payload: object = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ProjectAgentError(f"{PROJECT_AGENT_DIR}/{INDEX_FILE} is missing") from exc
    except json.JSONDecodeError as exc:
        raise ProjectAgentError(f"invalid {PROJECT_AGENT_DIR}/{INDEX_FILE}: {exc}") from exc

    return _parse_index(payload)


def _safe_document(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ProjectAgentError(
            f"project-agent document escapes {PROJECT_AGENT_DIR}: {relative}"
        ) from exc
    if not candidate.is_file():
        raise ProjectAgentError(f"project-agent document is missing: {relative}")
    return candidate


def infer_affected_languages(
    changed_paths: Iterable[str],
    *,
    explicit_languages: Iterable[str] = (),
    language_patterns: dict[str, list[str]] | None = None,
) -> tuple[str, ...]:
    explicit = _deduplicate(explicit_languages)
    unsupported = [language for language in explicit if language not in SUPPORTED_LANGUAGES]
    if unsupported:
        raise ProjectAgentError(f"unsupported language(s): {', '.join(unsupported)}")

    patterns: dict[str, tuple[str, ...]] = dict(DEFAULT_LANGUAGE_PATTERNS)
    for language, project_patterns in (language_patterns or {}).items():
        patterns[language] = _deduplicate((*patterns.get(language, ()), *project_patterns))

    inferred: list[str] = []
    changed = tuple(changed_paths)
    for language in SUPPORTED_LANGUAGES:
        if any(_matches(path, patterns.get(language, ())) for path in changed):
            inferred.append(language)

    return _deduplicate((*explicit, *inferred))


def validate_project_agent(project_root: Path) -> ProjectAgentHealth:
    root = project_agent_root(project_root)
    relative_root = PROJECT_AGENT_DIR
    if not root.is_dir():
        return ProjectAgentHealth(
            exists=False,
            root=relative_root,
            baseline_tokens=None,
            rule_count=0,
            inference_count=0,
            referenced_files=0,
            errors=(),
            warnings=(),
        )

    errors: list[ProjectAgentFinding] = []
    warnings: list[ProjectAgentFinding] = []

    baseline = root / BASELINE_FILE
    baseline_tokens: int | None = None
    if not baseline.is_file():
        errors.append(
            ProjectAgentFinding("error", f"{relative_root}/{BASELINE_FILE}", "required baseline is missing")
        )
    else:
        baseline_tokens = _tokens(baseline)
        if baseline_tokens > BASELINE_TOKEN_WARNING:
            warnings.append(
                ProjectAgentFinding(
                    "warning",
                    f"{relative_root}/{BASELINE_FILE}",
                    f"baseline is approximately {baseline_tokens} tokens; keep always-loaded guidance below {BASELINE_TOKEN_WARNING} when practical",
                )
            )

    payload: _ProjectAgentIndex | None = None
    try:
        payload = _read_index(root)
    except ProjectAgentError as exc:
        errors.append(
            ProjectAgentFinding("error", f"{relative_root}/{INDEX_FILE}", str(exc))
        )

    referenced: set[str] = set()
    if payload is not None:
        for rule in payload.get("rules", []):
            for relative in rule["load"]:
                referenced.add(relative)
                try:
                    _safe_document(root, relative)
                except ProjectAgentError as exc:
                    errors.append(
                        ProjectAgentFinding(
                            "error",
                            f"{relative_root}/{INDEX_FILE}",
                            str(exc),
                        )
                    )

        markdown_files = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*.md")
            if path.name != BASELINE_FILE
        }
        unindexed = sorted(markdown_files - referenced)
        if unindexed:
            warnings.append(
                ProjectAgentFinding(
                    "warning",
                    relative_root,
                    "unindexed Markdown guidance: " + ", ".join(unindexed),
                )
            )

    return ProjectAgentHealth(
        exists=True,
        root=relative_root,
        baseline_tokens=baseline_tokens,
        rule_count=len(payload.get("rules", [])) if payload else 0,
        inference_count=len(payload.get("infer", [])) if payload else 0,
        referenced_files=len(referenced),
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def select_project_agent(
    project_root: Path,
    *,
    changed_paths: Iterable[str] = (),
    explicit_concerns: Iterable[str] = (),
    explicit_languages: Iterable[str] = (),
) -> ProjectAgentSelection | None:
    root = discover_project_agent(project_root)
    if root is None:
        return None

    health = validate_project_agent(project_root)
    if health.errors:
        raise ProjectAgentError(
            "; ".join(f"{finding.path}: {finding.message}" for finding in health.errors)
        )

    payload = _read_index(root)
    changed = tuple(_normalise(path) for path in changed_paths)
    explicit = _deduplicate(concern.strip().lower() for concern in explicit_concerns if concern.strip())

    inferred_list: list[str] = []
    for rule in payload.get("infer", []):
        if any(_matches(path, rule["paths"]) for path in changed):
            inferred_list.extend(str(concern).lower() for concern in rule["concerns"])
    inferred = _deduplicate(inferred_list)
    concerns = _deduplicate((*explicit, *inferred))

    affected_languages = infer_affected_languages(
        changed,
        explicit_languages=explicit_languages,
        language_patterns=payload.get("language_patterns", {}),
    )

    documents: list[str] = [f"{PROJECT_AGENT_DIR}/{BASELINE_FILE}"]
    matched_rules: list[str] = []
    concern_set = set(concerns)

    for rule in payload.get("rules", []):
        paths = tuple(rule.get("paths", []))
        rule_concerns = {str(concern).lower() for concern in rule.get("concerns", [])}
        path_match = True if not paths else any(_matches(path, paths) for path in changed)
        concern_match = True if not rule_concerns else bool(concern_set & rule_concerns)
        if path_match and concern_match:
            matched_rules.append(rule["id"])
            for relative in rule["load"]:
                repo_relative = f"{PROJECT_AGENT_DIR}/{relative}"
                if repo_relative not in documents:
                    _safe_document(root, relative)
                    documents.append(repo_relative)

    document_paths = tuple(project_root.resolve() / relative for relative in documents)
    approximate_tokens = sum(_tokens(path) for path in document_paths)
    if approximate_tokens > SELECTED_TOKEN_WARNING:
        # Keep selection deterministic; doctor/inspect can surface size, but selection remains valid.
        pass

    digest = hashlib.sha256()
    digest.update((root / INDEX_FILE).read_bytes())
    digest.update(b"\0")
    for relative, path in zip(documents, document_paths, strict=True):
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")

    return ProjectAgentSelection(
        documents=tuple(documents),
        matched_rules=tuple(matched_rules),
        explicit_concerns=explicit,
        inferred_concerns=inferred,
        concerns=concerns,
        affected_languages=affected_languages,
        approximate_tokens=max(1, approximate_tokens),
        selection_digest=digest.hexdigest(),
    )
