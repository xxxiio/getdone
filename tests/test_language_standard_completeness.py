"""Contract tests for complete language and general engineering standards."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = {
    "python": ("pyproject.toml", "pytest", "docstrings"),
    "rust": ("cargo clippy", "Result", "rustdoc"),
    "cpp": ("RAII", "sanitizer", "Doxygen"),
    "dart-flutter": ("dart analyze", "widget tests", "///"),
    "q-kdbplus": ("vector", "PyKX", "null"),
    "typescript": ("strict", "unknown", "tsc --noEmit"),
}
REQUIRED_TOPICS = (
    "design and boundaries",
    "types and data",
    "errors and resources",
    "concurrency and state",
    "testing",
    "performance",
    "security",
    "public api documentation",
    "tooling and delivery",
)


class LanguageStandardCompletenessTests(unittest.TestCase):
    def test_all_supported_language_standards_exist_and_cover_required_topics(self) -> None:
        for language, phrases in LANGUAGES.items():
            with self.subTest(language=language):
                path = ROOT / "skill/standards/languages" / f"{language}.md"
                self.assertTrue(path.is_file())
                content = path.read_text(encoding="utf-8")
                lowered = content.lower()
                for topic in REQUIRED_TOPICS:
                    self.assertIn(f"### {topic}", lowered)
                for heading in (
                    "## Apply by impact",
                    "## Rules",
                    "## Review triggers",
                    "## Required response",
                    "## Exceptions",
                    "## Evidence",
                ):
                    self.assertIn(heading, content)
                for phrase in phrases:
                    self.assertIn(phrase, content)
                self.assertIn("current task or change-impact record", content)

    def test_general_standard_defines_core_programming_principles(self) -> None:
        content = (ROOT / "skill/standards/core.md").read_text(encoding="utf-8")
        for phrase in (
            "Single responsibility",
            "High cohesion",
            "Low coupling",
            "Dependency inversion",
            "Tell, do not ask",
            "Law of Demeter",
            "YAGNI",
            "DRY",
            "KISS",
        ):
            self.assertIn(phrase, content)

    def test_typescript_is_selectable(self) -> None:
        from getdone.context_selection import select_context

        selection = select_context(ROOT, "feature", "typescript")
        self.assertIn("skill/standards/languages/typescript.md", selection.documents)
        self.assertLessEqual(len(selection.documents), 8)


if __name__ == "__main__":
    unittest.main()
