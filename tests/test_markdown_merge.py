from __future__ import annotations

import json
import unittest
from pathlib import Path

import jsonschema

from getdone.markdown_merge import analyse_markdown_sections, parse_markdown_sections


class MarkdownMergeAnalysisTests(unittest.TestCase):
    def test_reports_added_removed_changed_and_reordered_sections(self) -> None:
        installed = """# Plan

Intro.

## Objective

Keep the service reliable.

## Validation

Run the old test suite.

## Local Notes

Project-owned detail.
"""
        available = """# Plan

Intro.

## Validation

Run the complete test suite.

## Objective

Keep the service reliable.

## Rollback

Describe rollback steps.
"""

        suggestion = analyse_markdown_sections(installed, available)
        changes = suggestion.changes

        self.assertTrue(suggestion.available)
        self.assertIn("added", {change.kind for change in changes})
        self.assertIn("removed", {change.kind for change in changes})
        self.assertIn("content-changed", {change.kind for change in changes})
        self.assertIn("reordered", {change.kind for change in changes})
        self.assertEqual(suggestion.summary["added"], 1)
        self.assertEqual(suggestion.summary["removed"], 1)
        self.assertEqual(suggestion.summary["content-changed"], 1)

    def test_detects_probable_heading_rename_when_content_is_preserved(self) -> None:
        installed = """# Task

## Validation commands

Run unit tests and repository validation.
"""
        available = """# Task

## Verification

Run unit tests and repository validation.
"""

        suggestion = analyse_markdown_sections(installed, available)
        renamed = [change for change in suggestion.changes if change.kind == "heading-changed"]

        self.assertEqual(len(renamed), 1)
        self.assertEqual(renamed[0].installed_heading, "Validation commands")
        self.assertEqual(renamed[0].available_heading, "Verification")
        self.assertGreaterEqual(renamed[0].confidence or 0.0, 0.8)

    def test_detects_heading_text_and_level_changes(self) -> None:
        suggestion = analyse_markdown_sections(
            "# Task\n\n## Validation\n\nRun checks.\n",
            "# Task\n\n### VALIDATION\n\nRun checks.\n",
        )
        changes = [change for change in suggestion.changes if change.kind == "heading-changed"]

        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].installed_level, 2)
        self.assertEqual(changes[0].available_level, 3)
        self.assertEqual(changes[0].confidence, 1.0)

    def test_repeated_headings_are_matched_by_content_before_occurrence_order(self) -> None:
        installed = """# Review

## Notes

Alpha details.

## Notes

Beta details.
"""
        available = """# Review

## Notes

Beta details.

## Notes

Alpha details.
"""

        suggestion = analyse_markdown_sections(installed, available)
        kinds = [change.kind for change in suggestion.changes]

        self.assertEqual(kinds.count("reordered"), 2)
        self.assertNotIn("content-changed", kinds)
        self.assertNotIn("added", kinds)
        self.assertNotIn("removed", kinds)

    def test_repeated_empty_headings_use_stable_occurrence_matching(self) -> None:
        installed = """# Review

## Notes

## Notes
"""
        available = """# Review

## Notes

## Notes
"""

        suggestion = analyse_markdown_sections(installed, available)

        self.assertEqual(suggestion.changes, ())
        self.assertEqual(suggestion.summary["unchanged"], 3)

    def test_ignores_fenced_code_headings_and_preserves_hash_in_title(self) -> None:
        sections = analyse_markdown_sections(
            "# C#\n\n```markdown\n## Not a section\n```\n",
            "# C#\n\n```markdown\n## Still not a section\n```\n",
        )

        parsed = parse_markdown_sections("# C#\n\n```markdown\n## Not a section\n```\n")
        self.assertEqual([section.heading for section in parsed], ["C#"])
        self.assertEqual([change.kind for change in sections.changes], ["content-changed"])
        self.assertEqual(sections.summary["added"], 0)
        self.assertEqual(sections.summary["removed"], 0)

    def test_result_matches_json_schema(self) -> None:
        suggestion = analyse_markdown_sections(
            "# Old\n\nBody.\n",
            "# New\n\nBody.\n",
        )
        root = Path(__file__).resolve().parents[1]
        schema = json.loads(
            (root / "skill/schemas" / "section-merge-suggestion.schema.json").read_text(
                encoding="utf-8"
            )
        )

        jsonschema.Draft202012Validator(schema).validate(suggestion.as_dict())

    def test_result_is_json_serialisable(self) -> None:
        suggestion = analyse_markdown_sections(
            "# Old\n\nBody.\n",
            "# New\n\nBody.\n",
        )

        json.dumps(suggestion.as_dict())


if __name__ == "__main__":
    unittest.main()
