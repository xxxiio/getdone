"""Contract tests for language-specific public API documentation standards."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
LANGUAGE_STANDARDS = {
    "python.md": ("docstrings", "PEP 257", "doctest"),
    "rust.md": ("rustdoc", "///", "cargo doc --no-deps"),
    "cpp.md": ("documentation comments", "Doxygen", "ownership"),
    "dart-flutter.md": ("documentation comments", "///", "dart doc"),
    "q-kdbplus.md": ("structured adjacent comments", "infinity semantics", "generated q reference"),
    "typescript.md": ("TSDoc/JSDoc", "unknown", "TypeDoc"),
}


class PublicApiDocumentationContractTests(unittest.TestCase):
    def test_core_acceptance_requires_public_api_documentation(self) -> None:
        content = (ROOT / "skill/acceptance/core.md").read_text()
        self.assertIn("Changed public APIs", content)
        self.assertIn("language-appropriate documentation comments", content)
        self.assertIn("generated API documentation", content)

    def test_every_language_standard_defines_documentation_rules(self) -> None:
        for filename, required_phrases in LANGUAGE_STANDARDS.items():
            with self.subTest(filename=filename):
                content = (ROOT / "skill/standards/languages" / filename).read_text()
                self.assertIn("changed public", content.lower())
                self.assertRegex(content, r"merely (repeat|restate)")
                self.assertIn("narrowly configured exclusions", content)
                for phrase in required_phrases:
                    self.assertIn(phrase, content)


if __name__ == "__main__":
    unittest.main()
