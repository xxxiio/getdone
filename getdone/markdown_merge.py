"""Read-only, section-aware comparison for project-owned Markdown templates."""

from __future__ import annotations

import difflib
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from typing import Any, Iterable

try:
    from getdone.markdown_sections import MarkdownSection, parse_markdown_sections
except ModuleNotFoundError:  # Direct import from the tooling directory.
    from markdown_sections import MarkdownSection, parse_markdown_sections


@dataclass(frozen=True)
class SectionChange:
    kind: str
    installed_heading: str | None = None
    available_heading: str | None = None
    installed_level: int | None = None
    available_level: int | None = None
    installed_occurrence: int | None = None
    available_occurrence: int | None = None
    installed_order: int | None = None
    available_order: int | None = None
    confidence: float | None = None
    reason: str = ""
    diff: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MarkdownMergeSuggestion:
    available: bool
    summary: dict[str, int]
    changes: tuple[SectionChange, ...]
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "available": self.available,
            "summary": dict(self.summary),
            "changes": [change.as_dict() for change in self.changes],
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class _SectionPair:
    installed: MarkdownSection
    available: MarkdownSection
    heading_changed: bool = False
    confidence: float | None = None
    heading_change_reason: str = ""


def _content_similarity(left: MarkdownSection, right: MarkdownSection) -> float:
    if not left.normalised_content and not right.normalised_content:
        return 1.0
    return difflib.SequenceMatcher(
        None,
        left.normalised_content,
        right.normalised_content,
    ).ratio()


def _greedy_pairs(
    installed: Iterable[MarkdownSection],
    available: Iterable[MarkdownSection],
) -> tuple[list[_SectionPair], set[int], set[int]]:
    left = list(installed)
    right = list(available)
    candidates = [
        (_content_similarity(old, new), abs(old.order - new.order), old, new)
        for old in left
        for new in right
    ]
    candidates.sort(key=lambda item: (-item[0], item[1], item[2].order, item[3].order))
    used_left: set[int] = set()
    used_right: set[int] = set()
    pairs: list[_SectionPair] = []
    for _, _, old, new in candidates:
        if old.order in used_left or new.order in used_right:
            continue
        pairs.append(_SectionPair(old, new))
        used_left.add(old.order)
        used_right.add(new.order)
    return pairs, used_left, used_right


def _match_same_headings(
    installed: tuple[MarkdownSection, ...],
    available: tuple[MarkdownSection, ...],
) -> tuple[list[_SectionPair], list[MarkdownSection], list[MarkdownSection]]:
    old_groups: dict[tuple[int, str], list[MarkdownSection]] = defaultdict(list)
    new_groups: dict[tuple[int, str], list[MarkdownSection]] = defaultdict(list)
    for section in installed:
        old_groups[(section.level, section.normalised_heading)].append(section)
    for section in available:
        new_groups[(section.level, section.normalised_heading)].append(section)

    pairs: list[_SectionPair] = []
    matched_old: set[int] = set()
    matched_new: set[int] = set()
    for key in sorted(old_groups.keys() & new_groups.keys()):
        group_pairs, used_old, used_new = _greedy_pairs(old_groups[key], new_groups[key])
        pairs.extend(group_pairs)
        matched_old.update(used_old)
        matched_new.update(used_new)
    return (
        pairs,
        [section for section in installed if section.order not in matched_old],
        [section for section in available if section.order not in matched_new],
    )


def _match_level_changes(
    old_sections: list[MarkdownSection],
    new_sections: list[MarkdownSection],
) -> tuple[list[_SectionPair], list[MarkdownSection], list[MarkdownSection]]:
    old_groups: dict[str, list[MarkdownSection]] = defaultdict(list)
    new_groups: dict[str, list[MarkdownSection]] = defaultdict(list)
    for section in old_sections:
        old_groups[section.normalised_heading].append(section)
    for section in new_sections:
        new_groups[section.normalised_heading].append(section)

    pairs: list[_SectionPair] = []
    matched_old: set[int] = set()
    matched_new: set[int] = set()
    for heading in sorted(old_groups.keys() & new_groups.keys()):
        group_pairs, used_old, used_new = _greedy_pairs(
            old_groups[heading],
            new_groups[heading],
        )
        pairs.extend(
            _SectionPair(
                pair.installed,
                pair.available,
                heading_changed=True,
                confidence=1.0,
                heading_change_reason="heading level changed",
            )
            for pair in group_pairs
        )
        matched_old.update(used_old)
        matched_new.update(used_new)
    return (
        pairs,
        [section for section in old_sections if section.order not in matched_old],
        [section for section in new_sections if section.order not in matched_new],
    )


def _match_probable_renames(
    old_sections: list[MarkdownSection],
    new_sections: list[MarkdownSection],
) -> tuple[list[_SectionPair], list[MarkdownSection], list[MarkdownSection]]:
    candidates: list[tuple[float, int, MarkdownSection, MarkdownSection]] = []
    for old in old_sections:
        for new in new_sections:
            if old.level != new.level or not old.normalised_content or not new.normalised_content:
                continue
            similarity = _content_similarity(old, new)
            if similarity >= 0.8:
                candidates.append((similarity, abs(old.order - new.order), old, new))
    candidates.sort(key=lambda item: (-item[0], item[1], item[2].order, item[3].order))

    matched_old: set[int] = set()
    matched_new: set[int] = set()
    pairs: list[_SectionPair] = []
    for similarity, _, old, new in candidates:
        if old.order in matched_old or new.order in matched_new:
            continue
        pairs.append(
            _SectionPair(
                old,
                new,
                heading_changed=True,
                confidence=similarity,
                heading_change_reason=(
                    "probable heading rename; direct section content is substantially preserved"
                ),
            )
        )
        matched_old.add(old.order)
        matched_new.add(new.order)
    return (
        pairs,
        [section for section in old_sections if section.order not in matched_old],
        [section for section in new_sections if section.order not in matched_new],
    )


def _section_diff(pair: _SectionPair) -> str:
    return "".join(
        difflib.unified_diff(
            pair.installed.content.splitlines(keepends=True),
            pair.available.content.splitlines(keepends=True),
            fromfile=f"installed:{pair.installed.heading}",
            tofile=f"available:{pair.available.heading}",
        )
    )


def _pair_changes(pair: _SectionPair) -> list[SectionChange]:
    changes: list[SectionChange] = []
    common = {
        "installed_heading": pair.installed.heading,
        "available_heading": pair.available.heading,
        "installed_level": pair.installed.level,
        "available_level": pair.available.level,
        "installed_occurrence": pair.installed.occurrence,
        "available_occurrence": pair.available.occurrence,
        "installed_order": pair.installed.order,
        "available_order": pair.available.order,
    }
    heading_text_changed = pair.installed.heading != pair.available.heading
    heading_level_changed = pair.installed.level != pair.available.level
    if pair.heading_changed or heading_text_changed or heading_level_changed:
        reason = pair.heading_change_reason or "heading text presentation changed"
        changes.append(
            SectionChange(
                "heading-changed",
                confidence=pair.confidence or 1.0,
                reason=reason,
                **common,
            )
        )
    if pair.installed.normalised_content != pair.available.normalised_content:
        changes.append(
            SectionChange(
                "content-changed",
                reason="matched section content differs",
                diff=_section_diff(pair),
                **common,
            )
        )
    return changes


def _reordered_orders(pairs: list[_SectionPair]) -> set[tuple[int, int]]:
    moved: set[tuple[int, int]] = set()
    for index, left in enumerate(pairs):
        for right in pairs[index + 1 :]:
            old_delta = left.installed.order - right.installed.order
            new_delta = left.available.order - right.available.order
            if old_delta * new_delta < 0:
                moved.add((left.installed.order, left.available.order))
                moved.add((right.installed.order, right.available.order))
    return moved


def _reorder_changes(pairs: list[_SectionPair]) -> list[SectionChange]:
    moved = _reordered_orders(pairs)
    return [
        SectionChange(
            "reordered",
            installed_heading=pair.installed.heading,
            available_heading=pair.available.heading,
            installed_level=pair.installed.level,
            available_level=pair.available.level,
            installed_occurrence=pair.installed.occurrence,
            available_occurrence=pair.available.occurrence,
            installed_order=pair.installed.order,
            available_order=pair.available.order,
            reason="matched section changes relative order",
        )
        for pair in pairs
        if (pair.installed.order, pair.available.order) in moved
    ]


def _unmatched_changes(
    kind: str,
    sections: Iterable[MarkdownSection],
) -> list[SectionChange]:
    changes: list[SectionChange] = []
    for section in sections:
        installed = kind == "removed"
        changes.append(
            SectionChange(
                kind,
                installed_heading=section.heading if installed else None,
                available_heading=None if installed else section.heading,
                installed_level=section.level if installed else None,
                available_level=None if installed else section.level,
                installed_occurrence=section.occurrence if installed else None,
                available_occurrence=None if installed else section.occurrence,
                installed_order=section.order if installed else None,
                available_order=None if installed else section.order,
                reason=(
                    "heading exists only in project-owned content"
                    if installed
                    else "heading exists only in the available template"
                ),
            )
        )
    return changes


def _summary(changes: list[SectionChange], pairs: list[_SectionPair]) -> dict[str, int]:
    counts = Counter(change.kind for change in changes)
    changed_pairs = {
        (change.installed_order, change.available_order)
        for change in changes
        if change.installed_order is not None and change.available_order is not None
    }
    return {
        "added": counts["added"],
        "removed": counts["removed"],
        "heading-changed": counts["heading-changed"],
        "content-changed": counts["content-changed"],
        "reordered": counts["reordered"],
        "unchanged": len(pairs) - len(changed_pairs),
    }


def _empty_suggestion() -> MarkdownMergeSuggestion:
    return MarkdownMergeSuggestion(
        False,
        {
            "added": 0,
            "removed": 0,
            "heading-changed": 0,
            "content-changed": 0,
            "reordered": 0,
            "unchanged": 0,
        },
        (),
        ("section-aware analysis requires ATX Markdown headings",),
    )


def _analysis_notes() -> tuple[str, ...]:
    return (
        "This is a two-way structural comparison, not a three-way automatic merge.",
        (
            "Probable heading renames require same-level sections with at least "
            "0.80 content similarity."
        ),
        "Repeated headings are matched by content similarity, then by stable document order.",
    )


def analyse_markdown_sections(installed: str, available: str) -> MarkdownMergeSuggestion:
    """Compare Markdown headings and direct section content without proposing writes."""

    old_sections = parse_markdown_sections(installed)
    new_sections = parse_markdown_sections(available)
    if not old_sections and not new_sections:
        return _empty_suggestion()

    pairs, unmatched_old, unmatched_new = _match_same_headings(old_sections, new_sections)
    level_changes, unmatched_old, unmatched_new = _match_level_changes(
        unmatched_old,
        unmatched_new,
    )
    renamed, unmatched_old, unmatched_new = _match_probable_renames(
        unmatched_old,
        unmatched_new,
    )
    pairs.extend(level_changes)
    pairs.extend(renamed)
    pairs.sort(key=lambda pair: (pair.installed.order, pair.available.order))

    changes = [change for pair in pairs for change in _pair_changes(pair)]
    changes.extend(_reorder_changes(pairs))
    changes.extend(_unmatched_changes("removed", unmatched_old))
    changes.extend(_unmatched_changes("added", unmatched_new))
    changes.sort(
        key=lambda change: (
            change.installed_order if change.installed_order is not None else 10**9,
            change.available_order if change.available_order is not None else 10**9,
            change.kind,
        )
    )
    return MarkdownMergeSuggestion(
        True,
        _summary(changes, pairs),
        tuple(changes),
        _analysis_notes(),
    )


def _change_label(change: SectionChange) -> str:
    old = change.installed_heading or "-"
    new = change.available_heading or "-"
    if change.kind == "heading-changed":
        return f"{old!r} -> {new!r}"
    heading = change.available_heading if change.kind == "added" else change.installed_heading
    if change.kind == "content-changed":
        heading = change.available_heading or change.installed_heading
    if change.kind == "reordered":
        heading = change.available_heading or change.installed_heading
    return repr(heading or "-")


def format_merge_suggestion(
    suggestion: MarkdownMergeSuggestion,
    *,
    indent: str = "  ",
) -> str:
    """Format a concise human-readable section comparison."""

    summary = suggestion.summary
    counts = ", ".join(
        f"{summary[key]} {key}"
        for key in ("added", "removed", "heading-changed", "content-changed", "reordered")
        if summary.get(key, 0)
    )
    lines = [f"{indent}section-summary: {counts or 'no structural changes'}"]
    for change in suggestion.changes:
        confidence = "" if change.confidence is None else f" confidence={change.confidence:.2f}"
        lines.append(
            f"{indent}  {change.kind}: {_change_label(change)}{confidence}"
        )
    for note in suggestion.notes:
        lines.append(f"{indent}  note: {note}")
    return "\n".join(lines)
