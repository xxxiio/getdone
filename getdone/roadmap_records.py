"""Parse and validate controlled roadmap milestone blocks."""

from __future__ import annotations

import re
from dataclasses import dataclass

try:
    from getdone.frontmatter import FrontmatterDocument
except ModuleNotFoundError as exc:
    if exc.name not in {"getdone", "getdone.frontmatter"}:
        raise
    from frontmatter import FrontmatterDocument

H2_PATTERN = re.compile(r"(?m)^## ([^\n]+)\s*$")
H3_PATTERN = re.compile(r"(?m)^### ([^\n]+)\s*$")
COMMENT = re.compile(r"(?s)<!--.*?-->")
MILESTONE_HEADING = re.compile(r"^MILESTONE-[0-9]{4}\s+—\s+\S.*$")
MILESTONE_ID = re.compile(r"^MILESTONE-[0-9]{4}$")
EXIT_ID = re.compile(r"^EC-[0-9]{3}$")
CRITERION = re.compile(r"(?m)^- \[[ xX]\] (?P<id>[A-Z]+-[0-9]{3}):\s+\S")
ROADMAP_METADATA = ("Status", "Outcome", "Why now", "Depends on")
ROADMAP_SUBHEADINGS = (
    "Scope",
    "Non-goals",
    "Exit criteria",
    "Evidence",
    "Next milestone",
)
MILESTONE_STATUSES = {
    "proposed",
    "ready",
    "active",
    "blocked",
    "completed",
    "deferred",
    "cancelled",
}


@dataclass(frozen=True)
class RoadmapMilestone:
    identifier: str
    status: str
    exit_criteria: tuple[str, ...]
    dependencies: tuple[str, ...]
    next_milestone: str | None


def roadmap_errors(document: FrontmatterDocument) -> list[str]:
    milestones, parse_errors = parse_roadmap(document.body)
    errors = list(parse_errors)
    status = document.data.get("status")
    if status == "current" and not milestones:
        errors.append("current roadmap must contain at least one milestone")
    active = [item.identifier for item in milestones if item.status == "active"]
    if len(active) > 1:
        errors.append("roadmap may contain at most one active milestone")
    current = document.data.get("current_milestone")
    expected = active[0] if len(active) == 1 else None
    if status == "current" and current != expected:
        errors.append(f"current_milestone must be {expected!r} for the active milestone set")
    identifiers = {item.identifier for item in milestones}
    status_by_id = {item.identifier: item.status for item in milestones}
    for item in milestones:
        errors.extend(_reference_errors(item, identifiers, status_by_id))
    if re.search(r"\b[0-9]{1,3}%", COMMENT.sub("", document.body)):
        errors.append("roadmap must use exit-criterion evidence, not percentage progress")
    return errors


def parse_roadmap(body: str) -> tuple[tuple[RoadmapMilestone, ...], tuple[str, ...]]:
    milestone_body = COMMENT.sub("", _h2_sections(body).get("Milestones", ""))
    headings = list(H3_PATTERN.finditer(milestone_body))
    milestones: list[RoadmapMilestone] = []
    errors: list[str] = []
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(milestone_body)
        title = match.group(1).strip()
        block = milestone_body[match.end() : end]
        if not MILESTONE_HEADING.fullmatch(title):
            errors.append(f"invalid milestone heading '{title}'")
            continue
        identifier = title.split(" — ", maxsplit=1)[0]
        milestone, block_errors = _parse_milestone_block(identifier, block)
        errors.extend(block_errors)
        if milestone is not None:
            milestones.append(milestone)
    if len({item.identifier for item in milestones}) != len(milestones):
        errors.append("roadmap milestone IDs must be unique")
    return tuple(milestones), tuple(errors)


def _h2_sections(body: str) -> dict[str, str]:
    matches = list(H2_PATTERN.finditer(body))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[match.group(1).strip()] = body[match.end() : end].strip()
    return sections


def _parse_milestone_block(
    identifier: str,
    block: str,
) -> tuple[RoadmapMilestone | None, list[str]]:
    errors: list[str] = []
    metadata = _metadata(block)
    missing = [key for key in ROADMAP_METADATA if key not in metadata]
    if missing:
        return None, [f"{identifier} missing metadata: {', '.join(missing)}"]
    status = metadata["Status"]
    if status not in MILESTONE_STATUSES:
        errors.append(f"{identifier} has invalid status '{status}'")
    subheadings = [value.strip() for value in re.findall(r"(?m)^#### ([^\n]+)$", block)]
    if subheadings != list(ROADMAP_SUBHEADINGS):
        errors.append(f"{identifier} H4 headings must be {list(ROADMAP_SUBHEADINGS)}")
    criterion_matches = list(CRITERION.finditer(block))
    criteria = tuple(match.group("id") for match in criterion_matches)
    if not criteria or any(not EXIT_ID.fullmatch(value) for value in criteria):
        errors.append(f"{identifier} exit criteria must use EC-NNN checklist IDs")
    evidence = _evidence_rows(block)
    for criterion in criteria:
        if criterion not in evidence:
            errors.append(f"{identifier} has no evidence row for {criterion}")
    if status == "completed":
        errors.extend(_completed_criterion_errors(identifier, criterion_matches, evidence))
    dependencies, dependency_errors = _dependency_ids(metadata["Depends on"])
    errors.extend(f"{identifier} {message}" for message in dependency_errors)
    next_milestone, next_errors = _next_milestone(block)
    errors.extend(f"{identifier} {message}" for message in next_errors)
    milestone = RoadmapMilestone(
        identifier,
        status,
        criteria,
        dependencies,
        next_milestone,
    )
    return milestone, errors


def _metadata(block: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for key in ROADMAP_METADATA:
        pattern = rf"(?m)^- \*\*{re.escape(key)}:\*\*\s+(.+)$"
        match = re.search(pattern, block)
        if match is not None:
            values[key] = match.group(1).strip()
    return values


def _evidence_rows(block: str) -> dict[str, str]:
    return {
        match.group(1): match.group(2).strip()
        for match in re.finditer(r"(?m)^- (EC-[0-9]{3}):\s+(.+)$", block)
    }


def _completed_criterion_errors(
    identifier: str,
    criteria: list[re.Match[str]],
    evidence: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    for match in criteria:
        criterion = match.group("id")
        if "[ ]" in match.group(0):
            errors.append(f"{identifier} is completed but {criterion} is unchecked")
        if evidence.get(criterion, "").casefold() in {"", "not available"}:
            errors.append(f"{identifier} is completed but {criterion} has no evidence")
    return errors


def _dependency_ids(value: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if value.casefold() == "none":
        return (), ()
    values = tuple(part.strip() for part in value.split(",") if part.strip())
    invalid = tuple(item for item in values if MILESTONE_ID.fullmatch(item) is None)
    valid = tuple(item for item in values if MILESTONE_ID.fullmatch(item))
    errors = tuple(f"has invalid dependency ID '{item}'" for item in invalid)
    return valid, errors


def _next_milestone(block: str) -> tuple[str | None, tuple[str, ...]]:
    match = re.search(
        r"(?ms)^#### Next milestone\s*\n(?P<value>.*?)(?=^#### |\Z)",
        block,
    )
    value = "" if match is None else COMMENT.sub("", match.group("value")).strip()
    if value.casefold() == "none":
        return None, ()
    if MILESTONE_ID.fullmatch(value):
        return value, ()
    return None, (f"has invalid next milestone '{value}'",)


def _reference_errors(
    item: RoadmapMilestone,
    identifiers: set[str],
    status_by_id: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    for dependency in item.dependencies:
        if dependency not in identifiers:
            errors.append(f"{item.identifier} references unknown dependency {dependency}")
        elif item.status == "active" and status_by_id[dependency] != "completed":
            errors.append(
                f"{item.identifier} is active before dependency {dependency} is completed"
            )
    if item.next_milestone is not None and item.next_milestone not in identifiers:
        errors.append(
            f"{item.identifier} references unknown next milestone {item.next_milestone}"
        )
    return errors
