#!/usr/bin/env python3
"""Validate controlled project records and their cross-record references."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

try:
    from getdone.frontmatter import FrontmatterDocument, parse_frontmatter
    from getdone.roadmap_records import parse_roadmap, roadmap_errors
except ModuleNotFoundError as exc:
    if exc.name not in {"getdone", "getdone.frontmatter", "getdone.roadmap_records"}:
        raise
    from frontmatter import FrontmatterDocument, parse_frontmatter
    from roadmap_records import parse_roadmap, roadmap_errors

CONTRACT_PATH = Path("skill/contracts/project-records.json")
SCHEMA_PATH = Path("skill/schemas/project-record-contracts.schema.json")
H2_PATTERN = re.compile(r"(?m)^## ([^\n]+)\s*$")
H3_PATTERN = re.compile(r"(?m)^### ([^\n]+)\s*$")
ORDERED_ITEM = re.compile(r"(?m)^\d+\.\s+\S")
BULLET_ITEM = re.compile(r"(?m)^-\s+\S")
CODE_BLOCK = re.compile(r"(?ms)^```[^\n]*\n(?P<body>.*?)^```\s*$")
COMMENT = re.compile(r"(?s)<!--.*?-->")
PLACEHOLDER = re.compile(r"<[^>]+>|\b(?:TBD|TO BE COMPLETED)\b", re.IGNORECASE)
CRITERION = re.compile(r"(?m)^- \[(?P<mark>[ xX])\] (?P<id>[A-Z]+-[0-9]{3}):\s+\S")
GATE_STATUSES = {"pass", "fail", "waived", "not-applicable", "not-run"}
IMPACT_VALUES = {"yes", "no", "unknown"}
INVARIANT_STATUSES = {"proposed", "active", "deprecated", "retired"}
IMPACT_GATE_REQUIREMENTS = {
    "public_api": "compatibility",
    "persisted_data": "migration",
    "configuration": "configuration",
    "dependencies": "dependency",
    "security_boundary": "security",
    "concurrency": "concurrency",
    "performance_sensitive": "performance",
    "user_interface": "ui",
    "deployment": "deployment",
}

@dataclass(frozen=True)
class RecordFinding:
    path: Path
    message: str


@dataclass(frozen=True)
class ContractRegistry:
    schema_version: int
    contract_version: str
    records: dict[str, dict[str, Any]]

    @property
    def templates(self) -> dict[str, str]:
        return {
            template: name
            for name, contract in self.records.items()
            for template in contract["templates"]
        }


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def load_record_contracts(root: Path) -> ContractRegistry:
    root = root.resolve()
    payload = _load_json(root / CONTRACT_PATH)
    schema = _load_json(root / SCHEMA_PATH)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(payload),
        key=lambda error: list(error.path),
    )
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ValueError(f"invalid project record contracts: {details}")
    return ContractRegistry(
        schema_version=payload["schema_version"],
        contract_version=payload["contract_version"],
        records=payload["records"],
    )


def _sections(body: str) -> tuple[list[str], dict[str, str]]:
    matches = list(H2_PATTERN.finditer(body))
    headings = [match.group(1).strip() for match in matches]
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[headings[index]] = body[match.end() : end].strip()
    return headings, sections


def _substantive(value: str) -> str:
    without_comments = COMMENT.sub("", value)
    return PLACEHOLDER.sub("", without_comments).strip()


def _frontmatter_errors(
    document: FrontmatterDocument,
    contract_name: str,
    contract: dict[str, Any],
    schema_version: int,
) -> list[str]:
    errors: list[str] = []
    data = document.data
    if data.get("record_contract") != contract_name:
        errors.append(f"record_contract must be '{contract_name}'")
    if data.get("record_schema_version") != schema_version:
        errors.append(f"record_schema_version must be {schema_version}")
    template = data.get("template")
    if template not in contract["templates"]:
        errors.append(f"template '{template}' is not allowed for {contract_name}")
    status = data.get("status")
    if status not in contract["statuses"]:
        errors.append(f"status '{status}' is not allowed for {contract_name}")
    allow_placeholders = status in contract["placeholder_statuses"]
    errors.extend(
        _required_field_errors(
            data, contract["required_frontmatter"], allow_placeholders=allow_placeholders
        )
    )
    return errors


def _required_field_errors(
    data: dict[str, Any],
    fields: dict[str, dict[str, Any]],
    *,
    allow_placeholders: bool,
) -> list[str]:
    errors: list[str] = []
    for name, rule in fields.items():
        value = data.get(name)
        field_type = rule["type"]
        if not _matches_type(value, field_type):
            errors.append(f"frontmatter.{name} must be {field_type}")
            continue
        if isinstance(value, str) and value:
            pattern = rule.get("pattern")
            placeholder = allow_placeholders and _is_frontmatter_placeholder(value)
            if pattern and not placeholder and re.fullmatch(pattern, value) is None:
                errors.append(f"frontmatter.{name} does not match {pattern}")
        if isinstance(value, list):
            errors.extend(_array_errors(name, value, rule))
    return errors


def _is_frontmatter_placeholder(value: str) -> bool:
    return value in {"YYYY-MM-DD"} or bool(PLACEHOLDER.search(value))


def _matches_type(value: Any, field_type: str) -> bool:
    if field_type == "string":
        return isinstance(value, str) and bool(value)
    if field_type == "nullable-string":
        return value is None or isinstance(value, str)
    if field_type == "string-array":
        return isinstance(value, list) and all(isinstance(item, str) for item in value)
    if field_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    return False


def _array_errors(name: str, values: list[str], rule: dict[str, Any]) -> list[str]:
    pattern = rule.get("item_pattern")
    if not pattern:
        return []
    return [
        f"frontmatter.{name} item '{value}' does not match {pattern}"
        for value in values
        if re.fullmatch(pattern, value) is None
    ]


def _rule_errors(heading: str, body: str, rule: str) -> list[str]:
    if rule == "text" and not _substantive(body):
        return [f"section '{heading}' contains only placeholder content"]
    if rule == "bullet-list" and not BULLET_ITEM.search(_substantive(body)):
        return [f"section '{heading}' must contain a bullet list"]
    if rule == "ordered-list" and not ORDERED_ITEM.search(_substantive(body)):
        return [f"section '{heading}' must contain an ordered list"]
    if rule == "code-block" and not _valid_code_block(body):
        return [f"section '{heading}' must contain a non-placeholder fenced code block"]
    if rule.startswith("criteria:"):
        return _criteria_errors(heading, body, rule.split(":", maxsplit=1)[1])
    if rule == "table" and len(_table_rows(body)) < 3:
        return [f"section '{heading}' must contain a Markdown table with a data row"]
    return []


def _valid_code_block(body: str) -> bool:
    return any(_substantive(match.group("body")) for match in CODE_BLOCK.finditer(body))


def _criteria_errors(heading: str, body: str, prefix: str) -> list[str]:
    matches = list(CRITERION.finditer(body))
    if not matches:
        return [f"section '{heading}' must contain checklist criteria with {prefix}-NNN IDs"]
    wrong = [match.group("id") for match in matches if not match.group("id").startswith(prefix)]
    return [f"section '{heading}' has invalid criterion ID '{value}'" for value in wrong]


def _table_rows(body: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            rows.append([cell.strip() for cell in stripped.strip("|").split("|")])
    return rows


def _content_errors(
    document: FrontmatterDocument,
    contract: dict[str, Any],
) -> list[str]:
    headings, sections = _sections(document.body)
    expected = contract["headings"]
    errors: list[str] = []
    if headings != expected:
        errors.append(f"H2 headings must exactly match this order: {expected}")
        return errors
    placeholder_allowed = document.data.get("status") in contract["placeholder_statuses"]
    for heading, rule in contract["section_rules"].items():
        body = sections.get(heading, "")
        if placeholder_allowed:
            continue
        errors.extend(_rule_errors(heading, body, rule))
    if document.data.get("status") in contract.get("completion_statuses", []):
        errors.extend(_unchecked_criteria_errors(sections))
    return errors


def _unchecked_criteria_errors(sections: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for heading, body in sections.items():
        for match in CRITERION.finditer(body):
            if match.group("mark") == " ":
                errors.append(
                    f"completed record has unchecked criterion {match.group('id')} in '{heading}'"
                )
    return errors


def validate_record_text(text: str, root: Path) -> list[str]:
    registry = load_record_contracts(root)
    try:
        document = parse_frontmatter(text)
    except ValueError as exc:
        return [str(exc)]
    contract_name = document.data.get("record_contract")
    if not isinstance(contract_name, str) or contract_name not in registry.records:
        return ["missing or unknown record_contract"]
    contract = registry.records[contract_name]
    errors = _frontmatter_errors(document, contract_name, contract, registry.schema_version)
    errors.extend(_content_errors(document, contract))
    errors.extend(_custom_errors(document, contract_name, contract))
    return errors


def _custom_errors(
    document: FrontmatterDocument,
    contract_name: str,
    contract: dict[str, Any],
) -> list[str]:
    custom = contract.get("custom_validator")
    if custom == "roadmap":
        return roadmap_errors(document)
    if custom == "acceptance-report":
        return _acceptance_errors(document, contract)
    if custom == "register":
        return _register_errors(document, contract)
    if custom == "todo-register":
        return _todo_errors(document)
    if custom == "change-impact":
        return _change_impact_errors(document, contract)
    if custom == "evidence-manifest":
        return _evidence_manifest_errors(document)
    if custom == "invariant-register":
        return _invariant_errors(document, contract)
    if custom == "execution-plan":
        return _execution_plan_errors(document)
    return []


def _acceptance_errors(
    document: FrontmatterDocument,
    contract: dict[str, Any],
) -> list[str]:
    _, sections = _sections(document.body)
    rows = _table_rows(sections.get("Gate results", ""))
    errors: list[str] = []
    expected = contract.get("table_headers", [])
    if rows and rows[0] != expected:
        errors.append(f"Gate results table header must be: {' | '.join(expected)}")
    statuses = [row[2] for row in rows[2:] if len(row) >= 4]
    errors.extend(
        f"Gate results contains invalid status '{status}'"
        for status in statuses
        if status not in GATE_STATUSES
    )
    if document.data.get("status") != "draft":
        errors.extend(_acceptance_status_errors(document.data.get("status"), statuses))
    return errors


def _acceptance_status_errors(report_status: object, statuses: list[str]) -> list[str]:
    if not statuses:
        return ["non-draft acceptance report must contain at least one gate result"]
    if report_status == "passed" and any(
        status not in {"pass", "not-applicable"} for status in statuses
    ):
        return ["passed acceptance report contains a non-passing gate"]
    if report_status == "failed" and "fail" not in statuses:
        return ["failed acceptance report must contain a failed gate"]
    if report_status == "waived" and "waived" not in statuses:
        return ["waived acceptance report must contain a waived gate"]
    if report_status == "incomplete" and not any(
        status in {"fail", "not-run"} for status in statuses
    ):
        return ["incomplete acceptance report must contain fail or not-run"]
    return []


def _register_errors(
    document: FrontmatterDocument,
    contract: dict[str, Any],
) -> list[str]:
    expected = contract.get("table_headers", [])
    rows = _table_rows(document.body)
    if not rows:
        return ["register must contain its controlled Markdown table"]
    if rows[0] != expected:
        return [f"register table header must be: {' | '.join(expected)}"]
    return []


def _change_impact_errors(
    document: FrontmatterDocument,
    contract: dict[str, Any],
) -> list[str]:
    _, sections = _sections(document.body)
    rows = _table_rows(sections.get("Impact classification", ""))
    expected = contract.get("table_headers", [])
    errors: list[str] = []
    if rows and rows[0] != expected:
        errors.append(f"Impact classification table header must be: {' | '.join(expected)}")
    if document.data.get("status") == "draft":
        return errors
    for row in rows[2:]:
        if len(row) < 4:
            continue
        impact, value, _reason, gate = row[:4]
        if value not in IMPACT_VALUES:
            errors.append(f"impact '{impact}' has invalid impact value '{value}'")
            continue
        required = IMPACT_GATE_REQUIREMENTS.get(impact)
        if required is None:
            errors.append(f"unknown impact dimension '{impact}'")
        elif value == "yes" and (not gate or gate == "none" or required not in gate.lower()):
            errors.append(f"impact '{impact}' requires an activated gate containing '{required}'")
    return errors


def _evidence_manifest_errors(document: FrontmatterDocument) -> list[str]:
    _, sections = _sections(document.body)
    acceptance = _table_rows(sections.get("Acceptance evidence", ""))
    gates = _table_rows(sections.get("Quality gate evidence", ""))
    errors: list[str] = []
    if acceptance and acceptance[0] != ["Criterion ID", "Status", "Evidence"]:
        errors.append("Acceptance evidence table header must be: Criterion ID | Status | Evidence")
    if gates and gates[0] != ["Gate", "Status", "Command or artefact", "Result"]:
        errors.append(
            "Quality gate evidence table header must be: "
            "Gate | Status | Command or artefact | Result"
        )
    if document.data.get("status") == "draft":
        return errors
    if len(acceptance) < 3:
        errors.append("non-draft evidence manifest must contain acceptance evidence")
    if len(gates) < 3:
        errors.append("non-draft evidence manifest must contain quality gate evidence")
    for row in acceptance[2:]:
        if len(row) < 3:
            continue
        criterion, status, evidence = row[:3]
        if status not in GATE_STATUSES:
            errors.append(f"criterion {criterion} has invalid status '{status}'")
        elif status == "pass" and not _substantive(evidence):
            errors.append(f"criterion {criterion} passed without evidence")
    for row in gates[2:]:
        if len(row) < 4:
            continue
        gate, status, command, result = row[:4]
        if status not in GATE_STATUSES:
            errors.append(f"gate {gate} has invalid status '{status}'")
        elif status == "pass" and (not _substantive(command) or not _substantive(result)):
            errors.append(f"gate {gate} passed without command/artefact and result evidence")
    return errors


def _invariant_errors(
    document: FrontmatterDocument,
    contract: dict[str, Any],
) -> list[str]:
    errors = _register_errors(document, contract)
    if document.data.get("status") == "draft":
        return errors
    rows = _table_rows(document.body)
    for row in rows[2:]:
        if len(row) < 6:
            continue
        identifier, _invariant, _scope, enforcement, trigger, status = row[:6]
        if re.fullmatch(r"INV-[0-9]{4}", identifier) is None:
            errors.append(f"invalid invariant ID '{identifier}'")
        if status not in INVARIANT_STATUSES:
            errors.append(f"invalid invariant status '{status}' for {identifier}")
        if status == "active" and (not _substantive(enforcement) or not _substantive(trigger)):
            errors.append(
                f"active invariant {identifier} requires enforcement and a review trigger"
            )
    return errors



SLICE_HEADING = re.compile(r"^SLICE-[0-9]{3}\s+—\s+\S.*$")
SLICE_DEPENDS = re.compile(r"(?m)^- \*\*Depends on:\*\*\s*(.+)$")
SLICE_CRITERION = re.compile(r"(?m)^- \[([ xX])\] (SC-[0-9]{3}):\s+\S")

def _execution_plan_errors(document: FrontmatterDocument) -> list[str]:
    if document.data.get("status") == "draft":
        return []
    _, sections = _sections(document.body)
    slice_body = sections.get("Slices", "")
    matches = list(H3_PATTERN.finditer(slice_body))
    identifiers: list[str] = []
    dependencies: dict[str, set[str]] = {}
    errors: list[str] = []
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        if SLICE_HEADING.fullmatch(title) is None:
            errors.append(f"invalid execution-plan slice heading '{title}'")
            continue
        identifier = title.split(" — ", 1)[0]
        if identifier in identifiers:
            errors.append(f"duplicate execution-plan slice ID '{identifier}'")
            continue
        identifiers.append(identifier)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(slice_body)
        block = slice_body[match.end():end]
        dep_match = SLICE_DEPENDS.search(block)
        if dep_match is None:
            errors.append(f"slice {identifier} is missing Depends on")
            dependencies[identifier] = set()
        else:
            raw = dep_match.group(1).strip()
            dependencies[identifier] = set() if raw == "none" else {item.strip() for item in raw.split(",") if item.strip()}
        if "**Advances exit criteria:**" not in block:
            errors.append(f"slice {identifier} is missing Advances exit criteria")
        if "**Validation tier:**" not in block:
            errors.append(f"slice {identifier} is missing Validation tier")
        if not SLICE_CRITERION.search(block):
            errors.append(f"slice {identifier} must contain SC-NNN acceptance criteria")
        if "#### Must not change" not in block:
            errors.append(f"slice {identifier} is missing Must not change")
    if not identifiers:
        errors.append("non-draft execution plan must contain at least one SLICE-NNN")
        return errors
    first = document.data.get("first_slice_id")
    if first not in identifiers:
        errors.append(f"first_slice_id '{first}' is not defined in Slices")
    known = set(identifiers)
    for identifier, refs in dependencies.items():
        for ref in refs:
            if ref not in known:
                errors.append(f"slice {identifier} depends on unknown slice {ref}")
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(ref in known and visit(ref) for ref in dependencies.get(node, set())):
            return True
        visiting.remove(node); visited.add(node); return False
    if any(visit(node) for node in identifiers if node not in visited):
        errors.append("execution-plan slice dependencies contain a cycle")
    return errors

def _todo_errors(document: FrontmatterDocument) -> list[str]:
    errors: list[str] = []
    for title in H3_PATTERN.findall(COMMENT.sub("", document.body)):
        if re.fullmatch(r"TODO-[0-9]{4}\s+—\s+\S.*", title.strip()) is None:
            errors.append(f"invalid TODO heading '{title.strip()}'")
    return errors


def validate_profile_record_templates(root: Path) -> list[str]:
    root = root.resolve()
    registry = load_record_contracts(root)
    errors: list[str] = []
    seen: set[str] = set()
    templates_root = root / "skill/bootstrap/templates"
    for path in sorted(templates_root.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        document = parse_frontmatter(text)
        template = document.data.get("template")
        contract_name = registry.templates.get(template) if isinstance(template, str) else None
        if contract_name is None:
            continue
        seen.add(template)
        for message in validate_record_text(text, root):
            errors.append(f"{path.relative_to(root)}: {message}")
    missing = sorted(set(registry.templates) - seen)
    errors.extend(
        f"record template is not present in bootstrap profiles: {name}"
        for name in missing
    )
    return errors


def validate_project_records(project_root: Path, skills_root: Path) -> list[RecordFinding]:
    project_root = project_root.resolve()
    registry = load_record_contracts(skills_root)
    findings: list[RecordFinding] = []
    documents: dict[Path, FrontmatterDocument] = {}
    agent_root = project_root / ".agent"
    if not agent_root.is_dir():
        return [RecordFinding(Path(".agent"), "project record directory is missing")]
    for path in sorted(agent_root.rglob("*.md")):
        relative = path.relative_to(project_root)
        text = path.read_text(encoding="utf-8")
        document = parse_frontmatter(text)
        template = document.data.get("template")
        if template not in registry.templates:
            continue
        documents[relative] = document
        for message in validate_record_text(text, skills_root):
            findings.append(RecordFinding(relative, message))
    findings.extend(_cross_record_findings(documents))
    return findings


def _cross_record_findings(
    documents: dict[Path, FrontmatterDocument],
) -> list[RecordFinding]:
    roadmap_path = Path(".agent/roadmap.md")
    next_path = Path(".agent/current/next-step.md")
    task_path = Path(".agent/current/task.md")
    acceptance_path = Path(".agent/current/acceptance.md")
    impact_path = Path(".agent/current/change-impact.md")
    evidence_path = Path(".agent/current/evidence.md")
    roadmap = documents.get(roadmap_path)
    if roadmap is None:
        return []
    milestones, _ = parse_roadmap(roadmap.body)
    milestone_map = {item.identifier: set(item.exit_criteria) for item in milestones}
    findings: list[RecordFinding] = []
    if next_step := documents.get(next_path):
        findings.extend(_next_step_references(next_path, next_step, milestone_map))
    if task := documents.get(task_path):
        findings.extend(_task_references(task_path, task, milestone_map))
    current_task = documents.get(task_path)
    if acceptance := documents.get(acceptance_path):
        findings.extend(_acceptance_references(acceptance_path, acceptance, current_task))
    for path in (impact_path, evidence_path):
        if record := documents.get(path):
            findings.extend(_task_bound_record_references(path, record, current_task))
    findings.extend(
        _current_state_consistency(
            roadmap,
            current_task,
            acceptance,
            documents.get(evidence_path),
        )
    )
    return findings


def _current_state_consistency(
    roadmap: FrontmatterDocument,
    task: FrontmatterDocument | None,
    acceptance: FrontmatterDocument | None,
    evidence: FrontmatterDocument | None,
) -> list[RecordFinding]:
    """Reject completion and active-work states that contradict their authorities."""

    if task is None:
        return []
    findings: list[RecordFinding] = []
    task_path = Path(".agent/current/task.md")
    task_status = task.data.get("status")
    milestone_id = task.data.get("milestone_id")
    current_milestone = roadmap.data.get("current_milestone")
    if task_status in {"ready", "active", "blocked"} and current_milestone is not None:
        if milestone_id != current_milestone:
            findings.append(
                RecordFinding(
                    task_path,
                    f"{task_status} task milestone_id must match current roadmap milestone "
                    f"'{current_milestone}'",
                )
            )
    if task_status == "completed":
        if acceptance is None or acceptance.data.get("status") not in {"passed", "waived"}:
            findings.append(
                RecordFinding(
                    task_path,
                    "completed task requires a passed or waived current acceptance report",
                )
            )
        if evidence is None or evidence.data.get("status") != "final":
            findings.append(
                RecordFinding(task_path, "completed task requires a final evidence manifest")
            )
    return findings


def _next_step_references(
    path: Path,
    document: FrontmatterDocument,
    milestones: dict[str, set[str]],
) -> list[RecordFinding]:
    status = document.data.get("status")
    if status == "proposed":
        return []
    milestone = document.data.get("milestone_id")
    if milestone not in milestones:
        return [RecordFinding(path, f"milestone_id '{milestone}' is not present in roadmap")]
    findings: list[RecordFinding] = []
    for criterion in document.data.get("advances_exit_criteria", []):
        if criterion not in milestones[milestone]:
            findings.append(
                RecordFinding(path, f"exit criterion '{criterion}' is not defined by {milestone}")
            )
    if not document.data.get("advances_exit_criteria"):
        findings.append(
            RecordFinding(
                path,
                "non-proposed next step must advance an exit criterion",
            )
        )
    return findings


def _task_references(
    path: Path,
    document: FrontmatterDocument,
    milestones: dict[str, set[str]],
) -> list[RecordFinding]:
    if document.data.get("status") == "proposed":
        return []
    milestone = document.data.get("milestone_id")
    if milestone not in milestones:
        return [RecordFinding(path, f"milestone_id '{milestone}' is not present in roadmap")]
    return []


def _acceptance_references(
    path: Path,
    document: FrontmatterDocument,
    task: FrontmatterDocument | None,
) -> list[RecordFinding]:
    if document.data.get("status") == "draft":
        return []
    expected = None if task is None else task.data.get("id")
    if document.data.get("task_id") != expected:
        return [RecordFinding(path, f"task_id must match current task '{expected}'")]
    return []


def _task_bound_record_references(
    path: Path,
    document: FrontmatterDocument,
    task: FrontmatterDocument | None,
) -> list[RecordFinding]:
    if document.data.get("status") == "draft":
        return []
    expected = None if task is None else task.data.get("id")
    if document.data.get("task_id") != expected:
        return [RecordFinding(path, f"task_id must match current task '{expected}'")]
    return []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate controlled project records.")
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--skills-root", type=Path, default=Path(__file__).resolve().parents[1])
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        findings = validate_project_records(args.project_root, args.skills_root)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for finding in findings:
        print(f"error: {finding.path}: {finding.message}", file=sys.stderr)
    if findings:
        print(f"record validation failed: {len(findings)} error(s)", file=sys.stderr)
        return 1
    print("record validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
