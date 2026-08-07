from __future__ import annotations

import json
import sys
import tempfile
import unittest
from contextlib import chdir
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_dictionary  # noqa: E402
import list_wordnets  # noqa: E402


class DictionaryTests(unittest.TestCase):
    def test_latin_wordnet_catalog(self) -> None:
        catalog = list_wordnets.load_catalog(ROOT / "languages" / "wordnets.json")
        languages = catalog["languages"]
        self.assertEqual(len(languages), 26)
        self.assertEqual(len(catalog["review_languages"]), 8)
        self.assertEqual(
            [item["code"] for item in languages if item.get("build")],
            ["ca", "cs", "en", "lt", "pl", "pt", "sk", "es"],
        )

    def test_small_round_trip_and_prefix_reset(self) -> None:
        words = [
            "dom",
            "domek",
            "domowy",
            "drabina",
            "ekran",
            "gra",
            "komputer",
            "monitor",
            "program",
            "slowo",
            "spektrum",
            "hangman",
            "zabawa",
            "zagadka",
            "zamek",
            "zegar",
            "zeszyt",
        ]
        blob = build_dictionary.encode(words)
        build_dictionary.verify(blob, words)
        self.assertLess(len(blob), sum(map(len, words)))

    def test_release_dictionary_build(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            with chdir(temp_path):
                manifest = build_dictionary.build(
                    ROOT / "data" / "words-pl-ascii.txt",
                    Path("build/pl"),
                    Path("build/pl/generated/dictionary_meta.h"),
                    language="pl",
                    asm48=Path("build/pl/generated/dictionary_blob.asm"),
                    asm128=Path("build/pl/generated/dictionary_banks.asm"),
                )
            self.assertEqual(manifest["zx48"]["words"], 4_000)
            self.assertEqual(manifest["zx128"]["words"], 20_000)
            self.assertLess(manifest["zx48"]["bytes"], 20_000)
            self.assertEqual(len(manifest["zx128"]["banks"]), 5)
            self.assertTrue(
                all(bank["bytes"] <= 16_384 for bank in manifest["zx128"]["banks"])
            )

            build_path = temp_path / "build" / "pl"
            loaded = json.loads((build_path / "dictionary-manifest.json").read_text())
            self.assertEqual(loaded["format"], "FC5/16")
            self.assertEqual(loaded["language"], "pl")
            self.assertEqual(loaded["source_count"], 20_000)
            self.assertTrue(loaded["zx48"]["fits"])
            self.assertTrue(loaded["zx128"]["fits"])
            assembly = (build_path / "generated" / "dictionary_blob.asm").read_text()
            self.assertIn("_dictionary_blob", assembly)
            self.assertIn('BINARY "build/pl/dict48.bin"', assembly)
            self.assertNotIn(temp_path.as_posix(), assembly)

    def test_rejects_impossible_language_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            with self.assertRaisesRegex(ValueError, "divide into 5 banks"):
                build_dictionary.build(
                    ROOT / "data" / "words-pl-ascii.txt",
                    temp_path,
                    temp_path / "dictionary_meta.h",
                    words_128_count=19_999,
                )


if __name__ == "__main__":
    unittest.main()
