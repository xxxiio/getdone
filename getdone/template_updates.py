"""Inspect project-local bootstrap templates without modifying the consuming project."""

from __future__ import annotations

import difflib
import re
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

try:
    from getdone.frontmatter import add_template_digest, parse_frontmatter, verify_template_digest
    from getdone.initialise_project import load_skills_version, render_text, repository_root
    from getdone.markdown_merge import MarkdownMergeSuggestion, analyse_markdown_sections
    from getdone.profiles import collect_profile_templates, load_profiles, resolve_profile
except ModuleNotFoundError:  # Direct import from the tooling directory.
    from frontmatter import add_template_digest, parse_frontmatter, verify_template_digest
    from initialise_project import load_skills_version, render_text, repository_root
    from markdown_merge import MarkdownMergeSuggestion, analyse_markdown_sections
    from profiles import collect_profile_templates, load_profiles, resolve_profile


_PROJECT_HEADING = re.compile(r"^# Project Context:\s*(.+?)\s*$", re.MULTILINE)
_REPOSITORY_BULLET = re.compile(r"^- Repository:\s*`([^`]+)`\s*$", re.MULTILINE)


@dataclass(frozen=True)
class RenderedTemplate:
    path: Path
    source_path: Path
    content: str


@dataclass(frozen=True)
class TemplateUpdate:
    path: Path
    status: str
    installed_version: str | None
    available_version: str | None
    safe_to_add: bool = False
    safe_to_replace: bool = False
    reason: str = ""
    diff: str = ""
    merge_suggestion: MarkdownMergeSuggestion | None = None

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["path"] = self.path.as_posix()
        payload["merge_suggestion"] = (
            None if self.merge_suggestion is None else self.merge_suggestion.as_dict()
        )
        return payload


def _project_metadata(
    project_root: Path,
    *,
    default_skills_reference: str,
) -> dict[str, str]:
    reference = project_root / ".agent" / "skills-reference.md"
    if not reference.is_file():
        raise FileNotFoundError(
            "project has no .agent/skills-reference.md; bootstrap profile cannot be resolved"
        )
    reference_text = reference.read_text(encoding="utf-8")
    document = parse_frontmatter(reference_text)
    profile = document.data.get("bootstrap_profile")
    if not isinstance(profile, str) or not profile:
        raise ValueError("skills-reference front matter has no bootstrap_profile")

    generated_at = document.data.get("generated_at")
    repository_match = _REPOSITORY_BULLET.search(reference_text)
    project_context = project_root / ".agent" / "project-context.md"
    project_name = project_root.name
    if project_context.is_file():
        heading_match = _PROJECT_HEADING.search(project_context.read_text(encoding="utf-8"))
        if heading_match:
            project_name = heading_match.group(1).strip()

    return {
        "profile": profile,
        "generated_at": generated_at if isinstance(generated_at, str) else date.today().isoformat(),
        "skills_reference": (
            repository_match.group(1)
            if repository_match is not None
            else default_skills_reference
        ),
        "project_name": project_name,
    }


def _version_tuple(value: str | None) -> tuple[int, int, int] | None:
    if value is None:
        return None
    parts = value.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        return None
    return int(parts[0]), int(parts[1]), int(parts[2])


def _diff(relative: Path, installed: str | None, available: str) -> str:
    before = [] if installed is None else installed.splitlines(keepends=True)
    after = available.splitlines(keepends=True)
    from_name = "/dev/null" if installed is None else f"a/{relative.as_posix()}"
    to_name = f"b/{relative.as_posix()}"
    return "".join(
        difflib.unified_diff(
            before,
            after,
            fromfile=from_name,
            tofile=to_name,
        )
    )


def render_profile_templates(
    project_root: Path,
    *,
    skills_root: Path | None = None,
    profile: str | None = None,
) -> tuple[str, dict[Path, RenderedTemplate]]:
    """Render the selected profile without writing any project files."""

    project_root = project_root.resolve()
    skills_root = (skills_root or repository_root()).resolve()
    metadata = _project_metadata(
        project_root,
        default_skills_reference=str(skills_root),
    )
    selected_profile = profile or metadata["profile"]

    profiles = load_profiles(skills_root)
    resolved_profile = resolve_profile(profiles, selected_profile)
    sources = collect_profile_templates(skills_root, resolved_profile, profiles=profiles)
    values = {
        "PROJECT_NAME": metadata["project_name"],
        "SKILLS_REPOSITORY": metadata["skills_reference"],
        "SKILLS_VERSION": load_skills_version(skills_root),
        "GENERATED_AT": metadata["generated_at"],
        "BOOTSTRAP_PROFILE": selected_profile,
        "BOOTSTRAP_PROFILE_VERSION": resolved_profile.version,
        "BOOTSTRAP_PROFILE_LINEAGE": " -> ".join(resolved_profile.lineage),
    }

    rendered: dict[Path, RenderedTemplate] = {}
    for relative, source_path in sorted(sources.items()):
        source_text = source_path.read_text(encoding="utf-8")
        content = add_template_digest(render_text(source_text, values))
        rendered[relative] = RenderedTemplate(relative, source_path, content)
    return selected_profile, rendered


StatusResult = tuple[str, str | None, str | None, bool, str]


def _metadata_status(
    destination_text: str,
    rendered: RenderedTemplate,
) -> tuple[StatusResult | None, str | None, str | None]:
    source_document = parse_frontmatter(rendered.content)
    destination_document = parse_frontmatter(destination_text)
    available_value = source_document.data.get("template_version")
    installed_value = destination_document.data.get("template_version")
    available = available_value if isinstance(available_value, str) else None
    installed = installed_value if isinstance(installed_value, str) else None
    source_template = source_document.data.get("template")
    installed_template = destination_document.data.get("template")

    if source_template is None or available is None:
        result = (
            "unmanaged-source",
            installed,
            available,
            False,
            "source template lacks template identity or version metadata",
        )
        return result, installed, available
    if installed_template is None or installed is None:
        result = (
            "untracked",
            installed,
            available,
            False,
            "project file predates managed template provenance",
        )
        return result, installed, available
    if installed_template != source_template:
        reason = f"project template '{installed_template}' differs from '{source_template}'"
        return ("template-mismatch", installed, available, False, reason), installed, available
    if not verify_template_digest(destination_text):
        result = (
            "modified",
            installed,
            available,
            False,
            "project-owned content differs from its generated template digest",
        )
        return result, installed, available
    return None, installed, available


def _version_status(installed: str, available: str) -> StatusResult:
    installed_key = _version_tuple(installed)
    available_key = _version_tuple(available)
    if installed_key is None or available_key is None:
        return (
            "invalid-version",
            installed,
            available,
            False,
            "template version is not semantic major.minor.patch",
        )
    if installed_key < available_key:
        return (
            "update-available",
            installed,
            available,
            True,
            "newer template is available and the project file is unmodified",
        )
    if installed_key > available_key:
        return (
            "ahead",
            installed,
            available,
            False,
            "project template version is newer than the shared source",
        )
    return (
        "current",
        installed,
        available,
        False,
        "project template matches the current managed version",
    )


def _classify_status(destination_text: str, rendered: RenderedTemplate) -> StatusResult:
    metadata_result, installed, available = _metadata_status(destination_text, rendered)
    if metadata_result is not None:
        return metadata_result
    if installed is None or available is None:
        raise AssertionError("managed template versions unexpectedly missing")
    return _version_status(installed, available)


def _missing_update(relative: Path, rendered: RenderedTemplate) -> TemplateUpdate:
    document = parse_frontmatter(rendered.content)
    version_value = document.data.get("template_version")
    version = version_value if isinstance(version_value, str) else None
    return TemplateUpdate(
        relative,
        "missing",
        None,
        version,
        safe_to_add=True,
        reason="template exists in the selected profile but not in the project",
        diff=_diff(relative, None, rendered.content),
    )


def _existing_update(
    relative: Path,
    destination_text: str,
    rendered: RenderedTemplate,
) -> TemplateUpdate:
    status, installed, available, safe_to_replace, reason = _classify_status(
        destination_text,
        rendered,
    )
    suggestion = (
        analyse_markdown_sections(destination_text, rendered.content)
        if status == "modified" and relative.suffix.casefold() == ".md"
        else None
    )
    return TemplateUpdate(
        relative,
        status,
        installed,
        available,
        safe_to_replace=safe_to_replace,
        reason=reason,
        diff="" if status == "current" else _diff(relative, destination_text, rendered.content),
        merge_suggestion=suggestion,
    )


def inspect_template_updates(
    project_root: Path,
    *,
    skills_root: Path | None = None,
    profile: str | None = None,
) -> tuple[TemplateUpdate, ...]:
    project_root = project_root.resolve()
    _, templates = render_profile_templates(
        project_root,
        skills_root=skills_root,
        profile=profile,
    )

    results: list[TemplateUpdate] = []
    for relative, rendered in templates.items():
        destination = project_root / relative
        if not destination.exists():
            results.append(_missing_update(relative, rendered))
            continue
        results.append(
            _existing_update(
                relative,
                destination.read_text(encoding="utf-8"),
                rendered,
            )
        )
    return tuple(results)
