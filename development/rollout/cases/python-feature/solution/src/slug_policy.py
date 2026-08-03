"""Slug rendering policy used by the rollout feature case."""

from __future__ import annotations

import re


def render_slug(value: str, *, separator: str = "-") -> str:
    """Render a lowercase slug using the requested separator."""
    if not separator:
        raise ValueError("separator must not be empty")
    words = re.findall(r"[a-z0-9]+", value.lower())
    return separator.join(words)
