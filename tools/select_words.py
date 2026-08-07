#!/usr/bin/env python3
"""Select recognisable Hangman words from SJP.PL using a frequency ranking."""

from __future__ import annotations

import argparse
import csv
import zipfile
from pathlib import Path

from normalize_words import unaccent_ascii

EXCLUDED_FRAGMENTS = (
    "kurw",
    "chuj",
    "pierd",
    "jeb",
    "cipa",
    "cipk",
    "kutas",
    "sperma",
    "dziwk",
    "skurw",
    "ruchacz",
)


def load_frequency(path: Path) -> dict[str, tuple[int, int]]:
    ranking: dict[str, tuple[int, int]] = {}
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["deleted"] != "0" or row["whyDeleted"] != "":
                continue
            word = row["word"].strip().lower()
            try:
                score = (-int(row["adjFreq"]), int(row["Rank"]))
            except ValueError:
                continue
            if word not in ranking or score < ranking[word]:
                ranking[word] = score
    return ranking


def load_lemmas(path: Path) -> set[str]:
    lemmas: set[str] = set()
    with zipfile.ZipFile(path) as archive, archive.open("odm.txt") as stream:
        for raw in stream:
            line = raw.decode("utf-8").strip()
            if not line:
                continue
            word = line.split(",", 1)[0].strip()
            if (
                word
                and word[0].islower()
                and word.isalpha()
                and 3 <= len(word) <= 15
            ):
                lemmas.add(word)
    return lemmas


def normalise(word: str) -> str:
    return unaccent_ascii(word)


def select(sjp_zip: Path, frequency_csv: Path, limit: int) -> list[str]:
    frequency = load_frequency(frequency_csv)
    lemmas = load_lemmas(sjp_zip)
    best: dict[str, tuple[tuple[int, int], str]] = {}

    for original in lemmas:
        if original not in frequency:
            continue
        word = normalise(original)
        if (
            not word.isascii()
            or not word.isalpha()
            or not 3 <= len(word) <= 15
            or not any(vowel in word for vowel in "aeiouy")
            or any(fragment in word for fragment in EXCLUDED_FRAGMENTS)
        ):
            continue
        candidate = (frequency[original], original)
        if word not in best or candidate < best[word]:
            best[word] = candidate

    ordered = [word for word, _ in sorted(best.items(), key=lambda item: (item[1], item[0]))]
    if len(ordered) < limit:
        raise ValueError(f"only {len(ordered)} suitable words, need {limit}")
    return ordered[:limit]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sjp-zip", type=Path, required=True)
    parser.add_argument("--frequency-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=20_000)
    args = parser.parse_args()

    words = select(args.sjp_zip, args.frequency_csv, args.limit)
    header = (
        "# Polish Hangman words in descending source-frequency order.\n"
        "# Diacritics are intentionally folded to ASCII for the ZX Spectrum game.\n"
        "# Sources and licences: see data/README.md.\n"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(header + "\n".join(words) + "\n", encoding="ascii")
    print(f"wrote {len(words)} words to {args.output}")


if __name__ == "__main__":
    main()
