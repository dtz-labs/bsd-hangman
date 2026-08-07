from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_locale  # noqa: E402
import import_wordnet  # noqa: E402
from normalize_words import unaccent_ascii  # noqa: E402


class LocaleAndNormalizationTests(unittest.TestCase):
    def test_every_locale_generates_ascii_header_with_license_key(self) -> None:
        messages = ROOT / "locales" / "messages.def"
        for locale_path in sorted((ROOT / "locales").glob("*.po")):
            with self.subTest(locale=locale_path.stem), tempfile.TemporaryDirectory() as temp:
                output = Path(temp)
                header = output / "locale.h"
                manifest = output / "locale.json"
                build_locale.build(
                    messages,
                    locale_path,
                    locale_path.stem,
                    locale_path.stem,
                    header,
                    manifest,
                )

                header_text = header.read_text(encoding="ascii")
                self.assertIn(
                    f'#define LOCALE_CODE "{locale_path.stem}"', header_text
                )
                self.assertIn(
                    '#define TXT_LICENSE_KEY "L  ',
                    header_text,
                )
                loaded = json.loads(manifest.read_text(encoding="ascii"))
                self.assertIn("A-Z", loaded["strings"]["ascii_notice"])

    def test_unaccent_folds_european_latin_text_to_ascii(self) -> None:
        examples = {
            "Lodz": "lodz",
            "Łódź": "lodz",
            "garçon": "garcon",
            "Straße": "strasse",
            "œuvre": "oeuvre",
            "Þing": "thing",
            "A\N{COMBINING OGONEK}": "a",
        }
        for source, expected in examples.items():
            with self.subTest(source=source):
                self.assertEqual(unaccent_ascii(source), expected)

    def test_wordnet_tab_import_deduplicates_after_unaccent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "wn.tab"
            source.write_text(
                "# sample OMW records\n"
                "00001740-n\tlemma\tŁódź\n"
                "00001741-n\tlemma\tlodz\n"
                "00001742-n\tlemma\tœuvre\n"
                "00001743-n\tdefinition\tnot a lemma\n",
                encoding="utf-8",
            )
            self.assertEqual(
                import_wordnet.import_words([source], 3, 15),
                ["lodz", "oeuvre"],
            )

    def test_wordnet_import_rejects_acronyms_before_lowercasing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "wn.tab"
            source.write_text(
                "00001740-n\tlemma\tCIO\n"
                "00001741-n\tlemma\tordinary\n"
                "00001742-n\tlemma\tLondon\n",
                encoding="utf-8",
            )
            self.assertEqual(
                import_wordnet.import_words([source], 3, 15),
                ["ordinary", "london"],
            )
            self.assertEqual(
                import_wordnet.import_words(
                    [source], 3, 15, reject_uppercase=True
                ),
                ["ordinary"],
            )

    def test_wordnet_lmf_xml_import(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "wordnet.xml"
            source.write_text(
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<LexicalResource xmlns="http://globalwordnet.org/schemas/wn-lmf/1.4">'
                '<Lexicon id="sample" label="Sample" language="fr">'
                '<LexicalEntry id="w1"><Lemma writtenForm="garçon" '
                'partOfSpeech="n"/></LexicalEntry>'
                '<LexicalEntry id="w2"><Lemma writtenForm="arc en ciel" '
                'partOfSpeech="n"/></LexicalEntry>'
                '</Lexicon></LexicalResource>',
                encoding="utf-8",
            )
            self.assertEqual(
                import_wordnet.import_words([source], 3, 15),
                ["garcon"],
            )


if __name__ == "__main__":
    unittest.main()
