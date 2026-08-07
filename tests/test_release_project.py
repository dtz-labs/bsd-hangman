from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ("pl", "en", "es", "ca", "lt", "sk", "cs", "pt")


class ReleaseProjectTests(unittest.TestCase):
    def test_release_matrix_has_eight_complete_editions(self) -> None:
        catalog = (ROOT / "languages" / "catalog.mk").read_text(encoding="utf-8")
        match = re.search(r"^BUILD_LANGUAGES \?= (.+)$", catalog, re.MULTILINE)
        self.assertIsNotNone(match)
        self.assertEqual(tuple(match.group(1).split()), LANGUAGES)

        for language in LANGUAGES:
            with self.subTest(language=language):
                self.assertTrue((ROOT / "languages" / f"{language}.mk").is_file())
                self.assertTrue((ROOT / "locales" / f"{language}.po").is_file())
                self.assertTrue((ROOT / "data" / f"words-{language}-ascii.txt").is_file())

    def test_every_shipped_dictionary_has_source_and_licence_mapping(self) -> None:
        notices = (ROOT / "THIRD_PARTY.md").read_text(encoding="utf-8")
        for language in LANGUAGES:
            with self.subTest(language=language):
                self.assertIn(f"| `{language}` |", notices)
                self.assertRegex(
                    notices,
                    rf"[0-9a-f]{{64}}  data/words-{language}-ascii\.txt",
                )
        self.assertTrue((ROOT / "LICENSES" / "README.md").is_file())
        self.assertTrue((ROOT / "data" / "LICENSE-GPL-3.0.txt").is_file())

    def test_release_workflow_builds_and_requires_sixteen_tapes(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("make tapes", workflow)
        self.assertIn('test "${#tap_files[@]}" -eq 16', workflow)
        self.assertIn("cp -R LICENSES", workflow)
        self.assertIn("data/LICENSE-GPL-3.0.txt", workflow)

    def test_pages_exposes_every_language_and_both_models(self) -> None:
        html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "site" / "app.js").read_text(encoding="utf-8")
        for language in LANGUAGES:
            with self.subTest(language=language):
                self.assertIn(f'value="{language}"', html)
        self.assertIn('value="48"', html)
        self.assertIn('value="128"', html)
        self.assertIn('"taps/hangman-" + language + "-" + machine + ".tap"', script)
        self.assertIn("https://buymeacoffee.com/mpasternak", html)


if __name__ == "__main__":
    unittest.main()
