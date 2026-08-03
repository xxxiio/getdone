#!/usr/bin/env python3
"""Build a compact, deterministic guidance selection for common task classes."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    from getdone.frontmatter import parse_frontmatter
except ModuleNotFoundError as exc:  # Direct execution from the tooling directory.
    if exc.name not in {"getdone", "getdone.frontmatter"}:
        raise
    from frontmatter import parse_frontmatter

TASK_WORKFLOWS = {
    "feature": "skill/workflows/feature/tdd-feature-development.md",
    "bug-fix": "skill/workflows/bug-fix/regression-first-bug-fix.md",
    "refactoring": "skill/workflows/refactoring/characterisation-first-refactoring.md",
    "investigation": "skill/workflows/general/technical-investigation.md",
    "project-planning": "skill/workflows/general/project-planning.md",
    "execution-planning": "skill/workflows/general/execution-planning.md",
}
TASK_GATES = {
    "feature": "skill/acceptance/change-types/feature.md",
    "bug-fix": "skill/acceptance/change-types/bug-fix.md",
    "refactoring": "skill/acceptance/change-types/refactoring.md",
    "project-planning": "skill/acceptance/change-types/project-planning.md",
    "execution-planning": "skill/acceptance/change-types/execution-planning.md",
}
LANGUAGES = {"python", "q-kdbplus", "cpp", "rust", "dart-flutter", "typescript"}
CORE_DOCUMENTS = (
    "skill/standards/core.md",
    "skill/acceptance/core.md",
)
CONDITIONAL_DOCUMENTS = (
    {
        "condition": "The task introduces common infrastructure or a design pattern.",
        "path": "skill/registry/reuse-catalogue.json",
    },
    {
        "condition": "The task performs a destructive action.",
        "path": "skill/policies/destructive-actions.md",
    },
    {
        "condition": "The task handles secrets or credentials.",
        "path": "skill/policies/secrets-and-credentials.md",
    },
    {
        "condition": "The task introduces an external dependency.",
        "path": "skill/policies/dependency-introduction.md",
    },
)


@dataclass(frozen=True)
class ContextSelection:
    task_class: str
    languages: tuple[str, ...]
    workflow: str
    documents: tuple[str, ...]
    conditional_documents: tuple[dict[str, str], ...]
    approximate_tokens: int
    selection_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 2,
            "task_class": self.task_class,
            "primary_language": self.languages[0],
            "languages": list(self.languages),
            "workflow": self.workflow,
            "documents": list(self.documents),
            "conditional_documents": list(self.conditional_documents),
            "approximate_tokens": self.approximate_tokens,
            "selection_digest": self.selection_digest,
        }


def _workflow_index(root: Path) -> dict[str, str]:
    index: dict[str, str] = {}
    for path in sorted((root / "skill/workflows").rglob("*.md")):
        data = parse_frontmatter(path.read_text(encoding="utf-8")).data
        workflow_id = data.get("id")
        if isinstance(workflow_id, str):
            index[workflow_id] = path.relative_to(root).as_posix()
    return index


def _workflow_chain(root: Path, workflow: str) -> tuple[str, ...]:
    index = _workflow_index(root)
    chain: list[str] = []
    current: str | None = workflow
    seen: set[str] = set()
    while current is not None:
        if current in seen:
            raise ValueError(f"workflow parent cycle detected at {current}")
        seen.add(current)
        chain.append(current)
        data = parse_frontmatter((root / current).read_text(encoding="utf-8")).data
        parent = data.get("parent")
        current = index.get(parent) if isinstance(parent, str) else None
        if isinstance(parent, str) and current is None:
            raise ValueError(f"unknown workflow parent: {parent}")
    return tuple(reversed(chain))


def _deduplicate(paths: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(paths))


def _selection_digest(root: Path, task_class: str, languages: Iterable[str], paths: Iterable[str]) -> str:
    digest = hashlib.sha256()
    digest.update(f"{task_class}\0".encode())
    for language in languages:
        digest.update(language.encode())
        digest.update(b"\0")
    for relative in paths:
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update((root / relative).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _approximate_tokens(root: Path, paths: Iterable[str]) -> int:
    characters = sum(len((root / path).read_text(encoding="utf-8")) for path in paths)
    return max(1, math.ceil(characters / 4))


def select_context(root: Path, task_class: str, languages: str | Iterable[str]) -> ContextSelection:
    root = root.resolve()
    if task_class not in TASK_WORKFLOWS:
        raise ValueError(f"unsupported task class: {task_class}")
    requested = (languages,) if isinstance(languages, str) else tuple(languages)
    selected_languages = tuple(dict.fromkeys(requested))
    if not selected_languages:
        raise ValueError("at least one language is required")
    unsupported = [language for language in selected_languages if language not in LANGUAGES]
    if unsupported:
        raise ValueError(f"unsupported language(s): {', '.join(unsupported)}")

    workflow = TASK_WORKFLOWS[task_class]
    documents: list[str] = [*_workflow_chain(root, workflow)]
    documents.extend(CORE_DOCUMENTS)
    if task_class in {"project-planning", "execution-planning"}:
        documents.append("skill/contracts/project-records.md")
    else:
        documents.extend(
            f"skill/standards/languages/{language}.md" for language in selected_languages
        )
    if gate := TASK_GATES.get(task_class):
        documents.append(gate)
    selected = _deduplicate(documents)
    missing = [path for path in selected if not (root / path).is_file()]
    if missing:
        raise ValueError(f"selected context contains missing documents: {', '.join(missing)}")

    return ContextSelection(
        task_class=task_class,
        languages=selected_languages,
        workflow=workflow,
        documents=selected,
        conditional_documents=CONDITIONAL_DOCUMENTS,
        approximate_tokens=_approximate_tokens(root, selected),
        selection_digest=_selection_digest(root, task_class, selected_languages, selected),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Select the minimum shared guidance for a task.")
    parser.add_argument("--repository-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--task-class", choices=sorted(TASK_WORKFLOWS), required=True)
    parser.add_argument(
        "--language",
        choices=sorted(LANGUAGES),
        action="append",
        required=True,
        help="Affected implementation language; repeat for polyglot changes.",
    )
    parser.add_argument("--json", action="store_true", help="Emit the selection manifest as JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    selection = select_context(args.repository_root, args.task_class, args.language)
    if args.json:
        print(json.dumps(selection.to_dict(), indent=2, sort_keys=True))
        return 0
    print(f"workflow: {selection.workflow}")
    print(f"approximate tokens: {selection.approximate_tokens}")
    for path in selection.documents:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
