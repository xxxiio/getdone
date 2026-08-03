"""ATX Markdown section parsing for template-lifecycle analysis."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

try:
    from getdone.frontmatter import split_frontmatter
except ModuleNotFoundError:  # Direct import from the tooling directory.
    from frontmatter import split_frontmatter

_HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.+?)(?:[ \t]+#+[ \t]*)?$")
_FENCE = re.compile(r"^ {0,3}(```+|~~~+)")
_SPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class MarkdownSection:
    heading: str
    normalised_heading: str
    level: int
    order: int
    occurrence: int
    line: int
    content: str
    normalised_content: str


def _normalise_heading(value: str) -> str:
    return _SPACE.sub(" ", value.strip()).casefold()


def _normalise_content(value: str) -> str:
    return _SPACE.sub(" ", value.strip())


def _heading_rows(text: str) -> list[tuple[int, str, int]]:
    _, body = split_frontmatter(text)
    rows: list[tuple[int, str, int]] = []
    fence_marker: str | None = None
    for line_number, line in enumerate(body.splitlines(), start=1):
        fence = _FENCE.match(line)
        if fence:
            marker = fence.group(1)[0]
            if fence_marker == marker:
                fence_marker = None
            elif fence_marker is None:
                fence_marker = marker
            continue
        if fence_marker is not None:
            continue
        match = _HEADING.match(line)
        if match:
            rows.append((line_number, match.group(2).strip(), len(match.group(1))))
    return rows


def parse_markdown_sections(text: str) -> tuple[MarkdownSection, ...]:
    """Parse ATX headings into flat direct-content sections."""

    _, body = split_frontmatter(text)
    lines = body.splitlines(keepends=True)
    rows = _heading_rows(text)
    occurrences: Counter[tuple[int, str]] = Counter()
    sections: list[MarkdownSection] = []
    for order, (line_number, heading, level) in enumerate(rows):
        end_line = rows[order + 1][0] - 1 if order + 1 < len(rows) else len(lines)
        content = "".join(lines[line_number:end_line])
        normalised_heading = _normalise_heading(heading)
        key = (level, normalised_heading)
        occurrences[key] += 1
        sections.append(
            MarkdownSection(
                heading=heading,
                normalised_heading=normalised_heading,
                level=level,
                order=order,
                occurrence=occurrences[key],
                line=line_number,
                content=content,
                normalised_content=_normalise_content(content),
            )
        )
    return tuple(sections)
