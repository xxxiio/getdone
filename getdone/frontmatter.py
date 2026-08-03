"""YAML front-matter parsing and project-template provenance helpers."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

import yaml

_FRONTMATTER_START = "---\n"
_DIGEST_KEY = "template_digest"


@dataclass(frozen=True)
class FrontmatterDocument:
    data: dict[str, Any]
    body: str
    raw_frontmatter: str | None

    @property
    def has_frontmatter(self) -> bool:
        return self.raw_frontmatter is not None


def _normalise_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def split_frontmatter(text: str) -> tuple[str | None, str]:
    text = _normalise_newlines(text)
    if not text.startswith(_FRONTMATTER_START):
        return None, text

    closing_index = text.find("\n---\n", len(_FRONTMATTER_START))
    if closing_index < 0:
        raise ValueError("unterminated YAML front matter")

    raw = text[len(_FRONTMATTER_START) : closing_index]
    body = text[closing_index + len("\n---\n") :]
    return raw, body


def parse_frontmatter(text: str) -> FrontmatterDocument:
    raw, body = split_frontmatter(text)
    if raw is None:
        return FrontmatterDocument({}, body, None)

    loaded = yaml.safe_load(raw)
    if loaded is None:
        data: dict[str, Any] = {}
    elif isinstance(loaded, dict):
        data = loaded
    else:
        raise ValueError("YAML front matter must be a mapping")
    return FrontmatterDocument(data, body, raw)


def strip_template_digest(text: str) -> str:
    raw, body = split_frontmatter(text)
    if raw is None:
        return _normalise_newlines(text)

    retained = [
        line
        for line in raw.splitlines()
        if not line.startswith(f"{_DIGEST_KEY}:")
    ]
    return f"---\n{'\n'.join(retained)}\n---\n{body}"


def calculate_template_digest(text: str) -> str:
    canonical = strip_template_digest(text).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def add_template_digest(text: str) -> str:
    document = parse_frontmatter(text)
    if not document.has_frontmatter:
        return _normalise_newlines(text)
    if "template" not in document.data or "template_version" not in document.data:
        return _normalise_newlines(text)

    without_digest = strip_template_digest(text)
    raw, body = split_frontmatter(without_digest)
    if raw is None:  # Defensive; the document was already known to have front matter.
        return without_digest

    digest = calculate_template_digest(without_digest)
    lines = raw.splitlines()
    insert_at = next(
        (index + 1 for index, line in enumerate(lines) if line.startswith("template_version:")),
        len(lines),
    )
    lines.insert(insert_at, f'{_DIGEST_KEY}: "{digest}"')
    return f"---\n{'\n'.join(lines)}\n---\n{body}"


def verify_template_digest(text: str) -> bool:
    try:
        document = parse_frontmatter(text)
    except (ValueError, yaml.YAMLError):
        return False
    expected = document.data.get(_DIGEST_KEY)
    return isinstance(expected, str) and expected == calculate_template_digest(text)
