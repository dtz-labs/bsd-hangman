# Hangman for ZX Spectrum

[![CI](https://github.com/dtz-labs/bsd-hangman/actions/workflows/ci.yml/badge.svg)](https://github.com/dtz-labs/bsd-hangman/actions/workflows/ci.yml)
[![Release](https://github.com/dtz-labs/bsd-hangman/actions/workflows/release.yml/badge.svg)](https://github.com/dtz-labs/bsd-hangman/releases)
[![BSD-3-Clause](https://img.shields.io/badge/code-BSD--3--Clause-informational)](LICENSE)

**[Play the latest release in your browser](https://dtz-labs.github.io/bsd-hangman/)** — choose one of eight languages and either Spectrum 48K or 128K. Every individual TAP is also available from [GitHub Releases](https://github.com/dtz-labs/bsd-hangman/releases).

[Support new ZX Spectrum software on Buy Me a Coffee](https://buymeacoffee.com/mpasternak).

ASCII-only Hangman inspired by BSD Games, released as independent ZX Spectrum
48K and 128K tapes in eight languages:

| code | edition | 48K words | 128K words |
| --- | --- | ---: | ---: |
| `pl` | Polish | 4,000 | 20,000 |
| `en` | English | 4,000 | 20,000 |
| `es` | Spanish | 4,000 | 19,000 |
| `ca` | Catalan | 4,000 | 20,000 |
| `lt` | Lithuanian | 4,000 | 8,500 |
| `sk` | Slovak | 4,000 | 16,000 |
| `cs` | Czech | 4,000 | 20,000 |
| `pt` | Portuguese | 4,000 | 20,000 |

Every edition explicitly says that it has no accents and accepts only `A-Z`.
Diacritics and Latin ligatures are folded while dictionaries are imported, so
every word works on an unmodified Spectrum keyboard.

## Playing

Each tape has four modes: short (3-4), medium (5-7), long (8-15), and all words
(3-15). There are seven incorrect guesses, matching BSD Hangman. A repeated
letter does not cost an attempt.

Every guess has a distinct 1-bit beeper cue: a short rising, coin-like sound
for a hit, a falling sound for a miss, and a chirp for a repeated letter. A
guess updates only the cells that changed; the whole display is cleared only
when a new round or menu starts.

After a round, Enter keeps the selected mode, `M` returns to the mode menu, and
`Q` exits. Press `L` in the mode menu to read the complete four-page BSD
licence and the original/ZX Spectrum credits.

## Build, run, and test

A sibling z88dk checkout is used by default. `make` builds all eight enabled
languages and both memory variants. Release automation produces exactly 16
TAP files:

```sh
make
make list-languages
make test
make smoke
```

Override the compiler location with `Z88DK=/path/to/z88dk`. Select a language
when starting ZEsarUX; the default remains Polish:

```sh
make RUN_LANGUAGE=en run-zx48
make RUN_LANGUAGE=en run-zx128
make RUN_LANGUAGE=es smoke
```

The finished tapes live under `build/<code>/`. For example, English produces
`build/en/hangman-en-48.tap` and `build/en/hangman-en-128.tap`; Polish now uses
the same project naming convention: `hangman-pl-48.tap` and
`hangman-pl-128.tap`.

The smoke test boots the selected real tape, walks through all four licence pages,
chooses medium words, then makes a known hit twice and a known miss. It verifies
translated menu text, credits, decoded word length, all three sounds, a black
border after every sound, partial redraw behavior, and a 256x192 screenshot.

## Gettext translations

UI localization uses GNU gettext as a build-time format, without linking a
gettext runtime into the Spectrum program. Canonical English messages and
stable contexts are in [locales/messages.def](locales/messages.def), the
translator template is [locales/hangman.pot](locales/hangman.pot), and each
edition has a `locales/<code>.po` catalog.

All eight currently shipped catalogs contain all 32 messages. “Complete” here
means mechanically complete, ASCII-safe, width-checked, tested, and buildable;
it does not claim that every translation has had independent native-speaker
proofreading. The wider WordNet catalog lists future candidates and is not a
claim that those languages are already translated.

```sh
make pot                 # extract a fresh .pot
make update-po           # merge it into every .po
make check-translations  # validate the catalogs
```

During each language build, Python compiles its `.po` into a small `locale.h`
containing only that edition's strings. The generator rejects missing entries,
non-ASCII output, lines wider than 32 characters, stat labels that leave no
room for numbers, and a licence key other than `L`. See
[languages/README.md](languages/README.md) for the complete language recipe.

## Dictionaries and language catalog

OMW tabs, plain UTF-8 word lists, and GWA WordNet-LMF XML can be normalized
with `tools/import_wordnet.py`. `tools/normalize_words.py` follows the same
rule-based idea as PostgreSQL `unaccent`, applies Unicode decomposition and
explicit Latin-letter expansions, and emits unique lowercase ASCII words.
`tools/build_dictionary.py` then compiles them to the byte-packed `FC5/16`
format.

```sh
make import-wordnet \
  IMPORT_LANGUAGE=en \
  WORDNET_FILES="/path/to/wordnet.xml.gz"
```

[languages/wordnets.json](languages/wordnets.json) catalogs 24 European and two
additional Latin-script lexical inputs. Eight further WordNets remain in a
source/licence review section. Greek, Cyrillic, Arabic, Hebrew, CJK, and Thai
inputs are deliberately outside this catalog. Run `make list-wordnets` for the
complete list.

`FC5/16` sorts words into blocks of 16. The first word in each block is stored
in full; following words store four-bit common-prefix and suffix lengths.
Suffix letters use five bits each (`a=1` through `z=26`). The 128K dictionary is
split over physical banks 0, 1, 3, 4, and 6; game code and the decompressor stay
in fixed RAM. Every build proves that the 48K budget and all five 16K banks fit.

See [data/README.md](data/README.md) for dictionary provenance, licences, and
attribution.

## Licence

The original BSD Hangman was written by Ken Arnold and carries the 1983/1993
Regents of the University of California BSD licence. The ZX Spectrum version
is copyright 2026 Michal Pasternak under the same BSD 3-Clause terms; see
[LICENSE](LICENSE). Word data is not relicensed as BSD: every dictionary and
TAP retains its upstream terms. The exact mapping, credits, modification notes,
source links, and checksums are in [THIRD_PARTY.md](THIRD_PARTY.md), with notices
under [LICENSES/](LICENSES/) and detailed provenance in [data/README.md](data/README.md).

Tagged releases build all 16 TAPs in the official z88dk container, validate
their dictionary and memory budgets, publish individual downloads plus a ZIP
containing the licences, and redeploy the browser emulator from that release.
