# Dictionary provenance

All committed game lists contain unique lowercase ASCII words of 3-15 letters.
The 48K build takes the leading, frequency-ranked subset; the 128K build uses
the configured larger subset and divides it into five independently compressed
banks.

| code | committed | 48K | 128K | lexical source |
| --- | ---: | ---: | ---: | --- |
| `pl` | 20,000 | 4,000 | 20,000 | SJP.PL `odmiany` + K7TRY frequency list |
| `en` | 20,000 | 4,000 | 20,000 | Open English WordNet 2025 |
| `es` | 20,000 | 4,000 | 19,000 | MCR 3.0 via OMW 1.4 |
| `ca` | 20,000 | 4,000 | 20,000 | MCR 3.0 via OMW 1.4 |
| `lt` | 8,500 | 4,000 | 8,500 | Lithuanian WordNet via OMW 1.4 |
| `sk` | 16,000 | 4,000 | 16,000 | Slovak WordNet via OMW 1.4 |
| `cs` | 20,000 | 4,000 | 20,000 | wordfreq 3.1.1 fallback |
| `pt` | 20,000 | 4,000 | 20,000 | OpenWN-PT via OMW 1.4 |

## Polish

`words-pl-ascii.txt` was generated on 2026-08-07 from:

- SJP.PL `odmiany`, release `sjp-odm-20260803.zip`, as the authority for
  accepted Polish headwords. This project selects its Apache License 2.0
  option: <https://sjp.pl/sl/odmiany/>.
- K7TRY/WordFreqLists Polish Word Frequency List, under GPL-3.0, to rank SJP
  headwords and reject rows marked deleted or classified as names:
  <https://github.com/K7TRY/WordFreqLists>.

The generated Polish selection is distributed under GPL-3.0; see
`LICENSE-GPL-3.0.txt`. The generator also requires at least one vowel and
removes a small explicit set of vulgar stems.

## WordNet editions

The English list comes from Open English WordNet 2025 (CC BY 4.0 plus the
underlying Princeton WordNet notice). Spanish and Catalan use the Multilingual
Central Repository 3.0 data (CC BY 3.0). The Lithuanian and Slovak OMW packages
offer their WordNet data under AGPL-3.0, CC BY-SA 3.0, or ODbL 1.0; this project
selects CC BY-SA 3.0. Portuguese uses OpenWN-PT under CC BY-SA 3.0, together
with the upstream Princeton WordNet and Wiktionary notices included by that
project.

The six source WordNets were normalized from their original UTF-8 lemmas and
ranked with `wordfreq==3.1.1` before truncation. All-caps acronyms are rejected
before case folding; Open English WordNet capitalization is also used to remove
proper-name lemmas. Relevant upstream attribution:

- John P. McCrae et al., Open English WordNet;
- Aitor Gonzalez-Agirre, Egoitz Laparra, and German Rigau, MCR 3.0 (2012);
- Radovan Garabik and Indre Pileckyte, Lithuanian WordNet (2013);
- Valeria de Paiva and Alexandre Rademaker, OpenWN-PT (2012);
- Francis Bond and Ryan Foster, Open Multilingual WordNet (2013).

Sources: <https://en-word.net/downloads>,
<https://github.com/omwn/omw-data/releases/tag/v1.4>, and the per-package
`LICENSE`/`citation.bib` files distributed by OMW. Exact notices and the
per-edition mapping are preserved in [`../LICENSES/`](../LICENSES/) and
[`../THIRD_PARTY.md`](../THIRD_PARTY.md).

## Frequency ranking and Czech fallback

`wordfreq` code is Apache-2.0 and its aggregated frequency data is CC BY-SA
4.0: <https://github.com/rspeer/wordfreq>. It ranks the common lemmas retained
for all six WordNet-derived lists.

The current Czech WordNet is not openly downloadable for redistribution, and
the older Czech WordNet has non-commercial/licensing constraints. Therefore
the Czech edition transparently uses the Czech `wordfreq` list directly rather
than claiming WordNet provenance. This choice is recorded in
`languages/wordnets.json`.

## Reproduction rules

`tools/normalize_words.py` applies Unicode decomposition plus explicit rules
for Latin letters and ligatures, then keeps only lowercase `a-z`. Source forms
that collapse to the same accentless spelling are merged. The release build
needs only the committed ASCII lists; large upstream archives are not copied
into the project.

`tools/import_wordnet.py` imports OMW tabs, plain lists, and WordNet-LMF XML.
`tools/import_wordfreq.py` generates the documented fallback. Each resulting
file embeds a short provenance header; every upstream licence and attribution
continues to apply to derived dictionary data and tapes containing it.
