# Adding a language edition

Eight editions are currently enabled: `pl en es ca lt sk cs pt`. A new
Latin-script edition needs a gettext catalog, an ASCII dictionary, and one Make
configuration.

## 1. Translate the interface

The English source messages live in `locales/messages.def`. If the game gains
or changes UI text, extract and merge the catalogs with:

```sh
make pot
make update-po
```

Create `locales/<code>.po` from `locales/hangman.pot` and translate every
context. Translations must use printable ASCII, fit a 32-character Spectrum
row. `ascii_notice` must explicitly say that accents are absent and input is
limited to `A-Z`; `license_key` must retain the `L` key.

Gettext is used only on the build host. `tools/build_locale.py` compiles the
selected `.po` into a generated C header, so no gettext library or multi-language
string table occupies Spectrum RAM.

## 2. Prepare the dictionary

Create `data/words-<code>-ascii.txt` with unique lowercase `a-z` words, 3-15
letters long. OMW `.tab`, plain UTF-8, and GWA WordNet-LMF `.xml` or `.xml.gz`
inputs can be imported with:

```sh
make import-wordnet \
  IMPORT_LANGUAGE=en \
  WORDNET_FILES="/path/to/wordnet.xml.gz /path/to/extra-lemmas.txt"
```

`tools/import_wordnet.py` removes accents, expands common Latin ligatures,
filters spaces, punctuation, and all-caps acronyms, then deduplicates after
folding. Use `--reject-uppercase` for sources whose capitalization reliably
marks proper names. With
`wordfreq==3.1.1` installed, `--frequency-language <code>` ranks retained
WordNet lemmas by common usage. `tools/import_wordfreq.py` is available when a
properly redistributable WordNet cannot be obtained. Always record source
licences and attribution in `data/README.md`.

## 3. Add the build configuration

Create `languages/<code>.mk`, for example:

```make
LANGUAGE_NAME := English
PROGRAM_NAME := hangman-en
LOCALE_PO := locales/en.po
DICTIONARY_WORDS := data/words-en-ascii.txt
DICTIONARY_WORDS_48 := 4000
DICTIONARY_WORDS_128 := 20000
DICTIONARY_MAX_48_BYTES := 20000
```

Add the code to `BUILD_LANGUAGES` in `catalog.mk` when it is release-ready.
`make all-languages` discovers every configuration, while a chosen matrix can
be tested with `make BUILD_LANGUAGES="pl en"`.

The build fails if a translation is incomplete or invalid, a configured word
count is missing, a length mode is empty, the 48K dictionary exceeds its byte
budget, or any 128K bank exceeds 16 KB. Use `make RUN_LANGUAGE=<code> smoke`
for both emulator variants of one edition, or `make smoke-all` for the full
release matrix.
