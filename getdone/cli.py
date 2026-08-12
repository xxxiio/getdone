"""Typer-based umbrella command for GetDone."""

from __future__ import annotations

import importlib.metadata
import json
import os
import shutil
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

from getdone import context_selection, project_records
from getdone.initialise_project import (
    BOOTSTRAP_PROFILE,
    initialise_project,
    repository_root,
)
from getdone.planning_prompts import planning_prompt
from getdone.project_agent import (
    ProjectAgentError,
    select_project_agent,
    validate_project_agent,
)
from getdone.project_status import project_status_summary, render_project_status
from getdone.validate_project import validate_project

app = typer.Typer(
    name="getdone",
    help="Structured, evidence-driven development workflows for coding agents.",
    no_args_is_help=True,
    add_completion=False,
    suggest_commands=True,
)
project_agent_app = typer.Typer(
    help="Inspect and validate the optional .project-agent project extension.",
    no_args_is_help=True,
)
app.add_typer(project_agent_app, name="project-agent")


class ProjectAgentDoctorMode(str, Enum):
    auto = "auto"
    required = "required"
    off = "off"


def _version() -> str:
    try:
        return importlib.metadata.version("getdone-dev")
    except importlib.metadata.PackageNotFoundError:
        version_file = repository_root() / "VERSION"
        return version_file.read_text(encoding="utf-8").strip() if version_file.is_file() else "unknown"


def _skills_root(value: Path | None) -> Path:
    if value is not None:
        return value.resolve()
    configured = os.environ.get("GETDONE_SKILLS_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return repository_root().resolve()


def _exit(code: int) -> None:
    if code:
        raise typer.Exit(code)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(_version())
        raise typer.Exit()


@app.callback()
def root(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show the installed GetDone version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """Run GetDone through one discoverable command tree."""

    del version


@app.command("init")
def init_command(
    project_root: Annotated[
        Path,
        typer.Option(help="Project directory to bootstrap. Defaults to the current directory."),
    ] = Path.cwd(),
    skills_root: Annotated[
        Path | None,
        typer.Option(help="Skill-pack root. Defaults to GETDONE_SKILLS_ROOT or the checkout."),
    ] = None,
    project_name: Annotated[str | None, typer.Option(help="Displayed project name.")] = None,
    skills_reference: Annotated[
        str | None,
        typer.Option(help="Portable skill-pack path or URL stored in project metadata."),
    ] = None,
    overlay: Annotated[
        list[Path] | None,
        typer.Option(help="Catalogue overlay to pin; repeat the option for multiple overlays."),
    ] = None,
    overwrite: Annotated[
        bool,
        typer.Option(help="Replace existing bootstrap-managed files."),
    ] = False,
) -> None:
    """Bootstrap the canonical full project-owned GetDone state."""

    try:
        result = initialise_project(
            project_root,
            BOOTSTRAP_PROFILE,
            overwrite=overwrite,
            skills_root=_skills_root(skills_root),
            project_name=project_name,
            skills_reference=skills_reference,
            overlay_paths=tuple(overlay or ()),
        )
    except (OSError, ValueError) as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from exc
    for path in result.created:
        typer.echo(f"created: {path}")
    for path in result.skipped:
        typer.echo(f"skipped existing: {path}")
    typer.echo(f"summary: {len(result.created)} created, {len(result.skipped)} skipped")


@app.command("validate")
def validate_command(
    project_root: Annotated[Path, typer.Option(help="Project directory to validate.")],
    skills_root: Annotated[Path | None, typer.Option(help="Skill-pack root.")] = None,
    profile: Annotated[str | None, typer.Option(help="Expected bootstrap profile.")] = None,
) -> None:
    """Validate project records, templates, and composition lock."""

    report = validate_project(
        project_root,
        skills_root=_skills_root(skills_root),
        profile=profile,
    )
    for finding in report.errors:
        typer.echo(f"error: {finding.path}: {finding.message}", err=True)
    for finding in report.warnings:
        typer.echo(f"warning: {finding.path}: {finding.message}")
    if report.errors:
        typer.echo(f"validation failed: {len(report.errors)} error(s)", err=True)
        raise typer.Exit(1)
    digest = report.composition_digest[:12] if report.composition_digest else "unavailable"
    overlays = ", ".join(report.overlay_versions) if report.overlay_versions else "none"
    typer.echo(
        f"validation passed: {report.managed_files} managed file(s), "
        f"{len(report.warnings)} warning(s); composition={digest}; overlays={overlays}"
    )


@app.command("guidance")
def guidance_command(
    task_class: Annotated[str, typer.Option(help="Task class, such as feature or bug-fix.")],
    language: Annotated[
        list[str] | None,
        typer.Option(
            "--language",
            help="Explicit affected language; repeat as needed. Known affected paths may infer more.",
        ),
    ] = None,
    project_root: Annotated[
        Path,
        typer.Option(help="Consuming project root used to discover .project-agent/."),
    ] = Path.cwd(),
    changed_path: Annotated[
        list[str] | None,
        typer.Option(
            "--changed-path",
            help=(
                "Known or anticipated affected project path; repeat as needed. "
                "Used only to route workflow and project guidance."
            ),
        ),
    ] = None,
    concern: Annotated[
        list[str] | None,
        typer.Option("--concern", help="Project-defined concern; repeat as needed."),
    ] = None,
    no_project_agent: Annotated[
        bool,
        typer.Option(help="Disable .project-agent discovery for this guidance selection."),
    ] = False,
    skills_root: Annotated[Path | None, typer.Option(help="Skill-pack root.")] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON.")] = False,
) -> None:
    """Select the minimum task-specific workflow and project guidance."""

    argv = [
        "--repository-root",
        str(_skills_root(skills_root)),
        "--project-root",
        str(project_root),
        "--task-class",
        task_class,
    ]
    for item in language or ():
        argv.extend(["--language", item])
    for item in changed_path or ():
        argv.extend(["--changed-path", item])
    for item in concern or ():
        argv.extend(["--concern", item])
    if no_project_agent:
        argv.append("--no-project-agent")
    if json_output:
        argv.append("--json")
    _exit(context_selection.main(argv))


@project_agent_app.command("validate")
def project_agent_validate_command(
    project_root: Annotated[
        Path,
        typer.Option(help="Project directory containing .project-agent/."),
    ] = Path.cwd(),
) -> None:
    """Validate the project-specific agent extension."""

    report = validate_project_agent(project_root.resolve())
    if not report.exists:
        typer.echo("error: .project-agent/ not found", err=True)
        raise typer.Exit(1)
    for finding in report.errors:
        typer.echo(f"error: {finding.path}: {finding.message}", err=True)
    for finding in report.warnings:
        typer.echo(f"warning: {finding.path}: {finding.message}")
    if report.errors:
        raise typer.Exit(1)
    tokens = report.baseline_tokens if report.baseline_tokens is not None else 0
    typer.echo(
        f"project-agent valid: baseline~{tokens} tokens; "
        f"{report.rule_count} rule(s); {report.inference_count} inference rule(s); "
        f"{report.referenced_files} referenced file(s); "
        f"{len(report.warnings)} warning(s)"
    )


@project_agent_app.command("inspect")
def project_agent_inspect_command(
    project_root: Annotated[
        Path,
        typer.Option(help="Project directory containing .project-agent/."),
    ] = Path.cwd(),
    changed_path: Annotated[
        list[str] | None,
        typer.Option("--changed-path", help="Affected project path; repeat as needed."),
    ] = None,
    concern: Annotated[
        list[str] | None,
        typer.Option("--concern", help="Explicit project concern; repeat as needed."),
    ] = None,
    language: Annotated[
        list[str] | None,
        typer.Option("--language", help="Explicit affected language; repeat as needed."),
    ] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON.")] = False,
) -> None:
    """Show inferred concerns, languages, and selected project guidance."""

    try:
        selection = select_project_agent(
            project_root.resolve(),
            changed_paths=changed_path or (),
            explicit_concerns=concern or (),
            explicit_languages=language or (),
        )
    except ProjectAgentError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from exc
    if selection is None:
        typer.echo("error: .project-agent/ not found", err=True)
        raise typer.Exit(1)
    if json_output:
        typer.echo(json.dumps(selection.to_dict(), indent=2, sort_keys=True))
        return
    typer.echo(f"languages: {', '.join(selection.affected_languages) or 'none'}")
    typer.echo(f"concerns: {', '.join(selection.concerns) or 'none'}")
    typer.echo(f"matched rules: {', '.join(selection.matched_rules) or 'none'}")
    typer.echo(f"approximate tokens: {selection.approximate_tokens}")
    for document in selection.documents:
        typer.echo(document)


@app.command("planning-prompt")
def planning_prompt_command(
    mode: Annotated[str, typer.Option(help="Planning mode: project or execution.")] = "project",
    skills_root: Annotated[Path | None, typer.Option(help="Skill-pack root.")] = None,
) -> None:
    """Print a ready-to-copy ChatGPT planning prompt."""

    try:
        typer.echo(planning_prompt(_skills_root(skills_root), mode), nl=False)
    except (OSError, ValueError) as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from exc


@app.command("records")
def records_command(
    project_root: Annotated[Path, typer.Option(help="Project directory to validate.")],
    skills_root: Annotated[Path | None, typer.Option(help="Skill-pack root.")] = None,
) -> None:
    """Validate controlled project records only."""

    _exit(
        project_records.main(
            ["--project-root", str(project_root), "--skills-root", str(_skills_root(skills_root))]
        )
    )


@app.command("status")
def status_command(
    project_root: Annotated[Path, typer.Option(help="Project directory to summarise.")],
    skills_root: Annotated[Path | None, typer.Option(help="Skill-pack root.")] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON.")] = False,
) -> None:
    """Render a read-only summary of current project records and their validation."""

    try:
        summary = project_status_summary(project_root, _skills_root(skills_root))
    except (OSError, ValueError) as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from exc
    if json_output:
        typer.echo(json.dumps(summary.as_dict(), indent=2, sort_keys=True))
    else:
        typer.echo(render_project_status(summary), nl=False)


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    status: str
    detail: str
    blocking: bool = False


def _doctor_checks(
    project_root: Path,
    skills_root: Path,
    project_agent_mode: ProjectAgentDoctorMode = ProjectAgentDoctorMode.auto,
) -> list[DoctorCheck]:
    checks: list[DoctorCheck] = []
    checks.append(DoctorCheck("GetDone installation", "pass", _version()))
    skill_ok = (skills_root / "skill/workflow-router.md").is_file() and (
        skills_root / "VERSION"
    ).is_file()
    checks.append(
        DoctorCheck(
            "Skill pack",
            "pass" if skill_ok else "fail",
            str(skills_root) if skill_ok else f"not found at {skills_root}",
            blocking=True,
        )
    )
    if skill_ok and (project_root / ".agent").is_dir():
        report = validate_project(project_root, skills_root=skills_root)
        checks.append(
            DoctorCheck(
                "Project records",
                "pass" if report.is_valid else "fail",
                f"{report.managed_files} managed; {len(report.errors)} error(s); "
                f"{len(report.warnings)} warning(s)",
                blocking=True,
            )
        )
    else:
        checks.append(
            DoctorCheck(
                "Project records",
                "skip",
                "project is not bootstrapped" if not (project_root / ".agent").is_dir() else "skill pack unavailable",
            )
        )
    if project_agent_mode is ProjectAgentDoctorMode.off:
        checks.append(
            DoctorCheck("Project agent extension", "skip", "disabled by --project-agent off")
        )
    else:
        project_agent_report = validate_project_agent(project_root)
        if not project_agent_report.exists:
            required = project_agent_mode is ProjectAgentDoctorMode.required
            checks.append(
                DoctorCheck(
                    "Project agent extension",
                    "fail" if required else "warn",
                    ".project-agent/ not found",
                    blocking=required,
                )
            )
        else:
            checks.append(
                DoctorCheck(
                    "Project agent extension",
                    "pass" if project_agent_report.is_valid else "fail",
                    (
                        f"{project_agent_report.rule_count} rule(s); "
                        f"{project_agent_report.inference_count} inference rule(s); "
                        f"{project_agent_report.referenced_files} referenced file(s)"
                    ),
                    blocking=True,
                )
            )
            tokens = project_agent_report.baseline_tokens or 0
            baseline_warning = next(
                (
                    finding
                    for finding in project_agent_report.warnings
                    if finding.path.endswith("/AGENTS.md")
                ),
                None,
            )
            checks.append(
                DoctorCheck(
                    "Project agent baseline",
                    "warn" if baseline_warning else "pass",
                    f"AGENTS.md ~{tokens} tokens",
                )
            )
            if project_agent_report.errors or project_agent_report.warnings:
                detail = (
                    f"{len(project_agent_report.errors)} error(s); "
                    f"{len(project_agent_report.warnings)} warning(s)"
                )
                checks.append(
                    DoctorCheck(
                        "Project agent health",
                        "fail" if project_agent_report.errors else "warn",
                        detail,
                        blocking=bool(project_agent_report.errors),
                    )
                )
    checks.append(
        DoctorCheck(
            "Git repository",
            "pass" if (project_root / ".git").exists() else "warn",
            str(project_root),
        )
    )
    for command, label in (("git", "Git"), ("python", "Python"), ("zensical", "Zensical")):
        executable = shutil.which(command)
        required = command in {"git", "python"}
        checks.append(
            DoctorCheck(
                f"{label} executable",
                "pass" if executable else ("fail" if required else "optional"),
                executable or "not installed",
                blocking=required,
            )
        )
    return checks


@app.command("doctor")
def doctor_command(
    project_root: Annotated[
        Path,
        typer.Option(help="Project directory to diagnose."),
    ] = Path.cwd(),
    skills_root: Annotated[Path | None, typer.Option(help="Skill-pack root.")] = None,
    project_agent: Annotated[
        ProjectAgentDoctorMode,
        typer.Option(
            help="Project-agent check mode: auto warns if absent, required fails, off skips."
        ),
    ] = ProjectAgentDoctorMode.auto,
) -> None:
    """Diagnose installation, skill-pack, project, project-agent, and optional tooling health."""

    checks = _doctor_checks(
        project_root.resolve(),
        _skills_root(skills_root),
        project_agent,
    )
    width = max(len(check.name) for check in checks)
    for check in checks:
        typer.echo(f"{check.name:<{width}}  {check.status:<8}  {check.detail}")
    if any(check.blocking and check.status == "fail" for check in checks):
        raise typer.Exit(1)




def main() -> None:
    """Run the GetDone command-line interface."""

    app()


if __name__ == "__main__":
    main()
