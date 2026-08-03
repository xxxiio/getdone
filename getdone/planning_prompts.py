"""Render ready-to-copy ChatGPT planning prompts from the skill pack."""

from __future__ import annotations

from pathlib import Path

PROMPT_PATHS = {
    "project": "skill/adapters/prompts/chatgpt-project-planning.md",
    "execution": "skill/adapters/prompts/chatgpt-execution-planning.md",
}


def planning_prompt(skills_root: Path, mode: str) -> str:
    """Return the canonical ChatGPT planning prompt for *mode*."""

    try:
        relative = PROMPT_PATHS[mode]
    except KeyError as exc:
        supported = ", ".join(sorted(PROMPT_PATHS))
        raise ValueError(f"unsupported planning mode '{mode}'; choose one of: {supported}") from exc
    path = skills_root.resolve() / relative
    if not path.is_file():
        raise ValueError(f"planning prompt is missing: {path}")
    return path.read_text(encoding="utf-8").strip() + "\n"
