"""Slug rendering policy used by the rollout feature case."""


def render_slug(value: str, *, separator: str = "-") -> str:
    """Render a lowercase slug using the requested separator."""
    raise NotImplementedError("feature not implemented")
