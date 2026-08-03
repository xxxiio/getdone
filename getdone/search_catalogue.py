#!/usr/bin/env python3
"""Search workflows, reusable components, patterns, decisions, and examples."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from getdone.catalogue import (
        ENTRY_KINDS,
        ENTRY_STATUSES,
        Catalogue,
        SearchResult,
        load_catalogue,
        resolve_catalogue_entry,
        search_catalogue,
        validate_catalogue,
    )
except ModuleNotFoundError as exc:  # Direct execution from the tooling directory.
    if exc.name not in {"getdone", "getdone.catalogue"}:
        raise
    from catalogue import (  # type: ignore[no-redef]
        ENTRY_KINDS,
        ENTRY_STATUSES,
        Catalogue,
        SearchResult,
        load_catalogue,
        resolve_catalogue_entry,
        search_catalogue,
        validate_catalogue,
    )


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _result_payload(result: SearchResult) -> dict[str, object]:
    entry = result.entry
    return {
        "id": entry.entry_id,
        "kind": entry.kind,
        "title": entry.title,
        "status": entry.status,
        "summary": entry.summary,
        "path": entry.path.as_posix(),
        "source": entry.source,
        "score": result.score,
        "tags": list(entry.tags),
        "languages": list(entry.languages),
        "use_when": list(entry.use_when),
        "avoid_when": list(entry.avoid_when),
        "related": list(entry.related),
        "aliases": list(entry.aliases),
        "introduced_in": entry.introduced_in,
        "deprecated_in": entry.deprecated_in,
        "replaced_by": entry.replaced_by,
        "matched_alias": result.matched_alias,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search the getdone catalogue.")
    parser.add_argument("--repository-root", type=Path, default=repository_root())
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--query", default="", help="Terms describing the task or design need.")
    selector.add_argument("--id", dest="entry_id", help="Resolve one canonical ID or alias.")
    parser.add_argument("--overlay", action="append", type=Path, default=[])
    parser.add_argument("--kind", action="append", choices=ENTRY_KINDS)
    parser.add_argument("--language", action="append")
    parser.add_argument("--tag", action="append")
    parser.add_argument("--status", action="append", choices=ENTRY_STATUSES)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def _print_human(
    results: tuple[SearchResult, ...],
    source_versions: dict[str, str],
) -> None:
    if not results:
        print("No catalogue entries matched.")
        return
    for result in results:
        entry = result.entry
        alias_text = f" resolved from {result.matched_alias}" if result.matched_alias else ""
        print(f"{entry.entry_id} [{entry.kind}] score={result.score:g}{alias_text}")
        print(f"  {entry.title}: {entry.summary}")
        version = source_versions.get(entry.source, "unknown")
        print(f"  source: {entry.source}@{version}; path: {entry.path}")
        print(f"  status: {entry.status}; introduced: {entry.introduced_in}")
        if entry.replaced_by is not None:
            print(f"  replacement: {entry.replaced_by}")
        print(f"  tags: {', '.join(entry.tags)}")


def _search(args: argparse.Namespace, catalogue: Catalogue) -> tuple[SearchResult, ...]:
    if args.entry_id is not None:
        result = resolve_catalogue_entry(catalogue, args.entry_id)
        return () if result is None else (result,)
    return search_catalogue(
        catalogue,
        args.query,
        kinds=None if args.kind is None else set(args.kind),
        languages=None if args.language is None else set(args.language),
        tags=None if args.tag is None else set(args.tag),
        statuses=None if args.status is None else set(args.status),
        limit=args.limit,
    )


def _json_payload(
    args: argparse.Namespace,
    catalogue: Catalogue,
    results: tuple[SearchResult, ...],
) -> dict[str, object]:
    return {
        "schema_version": 3,
        "catalogue_version": catalogue.version,
        "workflow_registry_version": catalogue.workflow_registry_version,
        "sources": list(catalogue.sources),
        "source_versions": dict(catalogue.source_versions),
        "query": args.query,
        "requested_id": args.entry_id,
        "filters": {
            "kinds": sorted(args.kind or []),
            "languages": sorted(args.language or []),
            "tags": sorted(args.tag or []),
            "statuses": sorted(args.status or []),
        },
        "count": len(results),
        "results": [_result_payload(result) for result in results],
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if args.limit < 1:
        print("error: --limit must be at least 1", file=sys.stderr)
        return 2

    root = args.repository_root.resolve()
    try:
        catalogue = load_catalogue(root, overlay_paths=tuple(args.overlay))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(exc, file=sys.stderr)
        return 1
    errors = validate_catalogue(root, catalogue)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    results = _search(args, catalogue)
    if args.as_json:
        print(json.dumps(_json_payload(args, catalogue, results), indent=2))
    else:
        _print_human(results, dict(catalogue.source_versions))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
