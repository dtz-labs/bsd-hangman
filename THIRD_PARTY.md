# Third-party data, licences, and attribution

The Hangman program code is licensed under BSD-3-Clause. Dictionary data is
not relicensed under BSD: each committed word list and each TAP containing it
retains the terms below. The lists are modified extracts: lemmas were selected,
ranked, stripped of non-word entries, converted to lowercase ASCII without
accents, deduplicated, truncated, and compressed for the ZX Spectrum.

## Shipped dictionaries

| Edition | Lexical source | Licence selected for this distribution | Frequency source |
| --- | --- | --- | --- |
| `pl` | SJP.PL `odmiany` (`sjp-odm-20260803.zip`) | Apache-2.0 | K7TRY/WordFreqLists, GPL-3.0 |
| `en` | Open English WordNet 2025 | CC BY 4.0 and the Princeton WordNet notice | wordfreq 3.1.1 |
| `ca` | MCR 3.0 Catalan via OMW 1.4 | CC BY 3.0 | wordfreq 3.1.1 |
| `es` | MCR 3.0 Spanish via OMW 1.4 | CC BY 3.0 | wordfreq 3.1.1 |
| `lt` | Lithuanian WordNet via OMW 1.4 | CC BY-SA 3.0 (selected from the upstream alternatives) | wordfreq 3.1.1 |
| `sk` | Slovak WordNet via OMW 1.4 | CC BY-SA 3.0 (selected from the upstream alternatives) | wordfreq 3.1.1 |
| `cs` | wordfreq 3.1.1 Czech data | CC BY-SA 4.0 | wordfreq 3.1.1 |
| `pt` | OpenWN-PT via OMW 1.4 | CC BY-SA 3.0, Princeton WordNet, and Wiktionary notices | wordfreq 3.1.1 |

The Polish selection uses K7TRY frequency data under GPL-3.0. The committed
Polish word list and TAPs containing that list are therefore distributed with
the GPL-3.0 notice in
[`data/LICENSE-GPL-3.0.txt`](data/LICENSE-GPL-3.0.txt). The reusable program
source remains available separately under BSD-3-Clause.

The WordNet-derived lists use wordfreq only as a ranking and selection aid.
The Czech list is extracted directly from wordfreq and is distributed under
CC BY-SA 4.0. In both cases credit is due to Robyn Speer and the upstream
corpora listed in [`LICENSES/wordfreq-NOTICE.txt`](LICENSES/wordfreq-NOTICE.txt).

## Required attribution

- Open English WordNet: Copyright 2019-present, the Open English WordNet Team.
  Source: <https://en-word.net/downloads>. Cite John P. McCrae et al.
- Princeton WordNet: WordNet 3.0 Copyright 2006 by Princeton University.
- Multilingual Central Repository 3.0: Aitor Gonzalez-Agirre, Egoitz Laparra,
  and German Rigau (2012). Source: <https://adimen.si.ehu.es/web/MCR/>.
- Lithuanian WordNet: Radovan Garabik and Indre Pileckyte (2013).
- Slovak WordNet: Slovak National Corpus, <https://korpus.sk/WordNet_en.html>.
- OpenWN-PT: Valeria de Paiva and Alexandre Rademaker (2012), with Gerard de
  Melo's contribution. Source: <https://github.com/omwn/omw-data>.
- Open Multilingual WordNet: Francis Bond and Ryan Foster (2013). Release used:
  <https://github.com/omwn/omw-data/releases/tag/v1.4>.
- wordfreq: Copyright 2022 Robyn Speer. Source:
  <https://github.com/rspeer/wordfreq/tree/v3.1.1>.
- SJP.PL `odmiany`: <https://sjp.pl/sl/odmiany/>.
- K7TRY/WordFreqLists: <https://github.com/K7TRY/WordFreqLists>.

Exact upstream notices are preserved under [`LICENSES/`](LICENSES/). The
canonical provenance and reproducibility notes live in
[`data/README.md`](data/README.md).

## Browser emulator

The GitHub Pages build downloads JSSpeccy 3 v3.2.0-timex.2 from
<https://github.com/dtz-labs/jsspeccy3>. JSSpeccy 3 is GPL-3.0; its `COPYING`,
`README.md`, and `CHANGELOG.md` are deployed beside the emulator. JSSpeccy is a
separate browser program and is not linked into the ZX Spectrum TAP files.

## Dictionary file checksums

```text
8c2aeefa3861caf4810127d3974ef503025f707314c63d5aa35d916981492dc4  data/words-ca-ascii.txt
5b5bf69387cc8a8dc0b3677a9fb9bbe2dc0afd6ff406cf41c4f3bc76d6d06011  data/words-cs-ascii.txt
3940f977997bb5d2ccdbf1f88cc90aaef93ec474347834d2215de9be0048afa9  data/words-en-ascii.txt
1c5cd054d68577a9a4dcf37fec85859315a727ca996709e6deeb24650f6589a3  data/words-es-ascii.txt
9aff5d58492823bfdd61df77ff45f31eab2623109e5a3cb4fa11b3e5f7eb61d8  data/words-lt-ascii.txt
b040627bc0ec6ebe6f8324a675f63a276334fa67c387e81e1dd78f9e4426fdb8  data/words-pl-ascii.txt
b5912b8588f02a596439c5e2d936a50e9b634a90fa6dab693091f141e4c7f440  data/words-pt-ascii.txt
d700aae8c89ae50641d478fa813beed7bd73dc9c1eab905dc3f50ba97ecc4d51  data/words-sk-ascii.txt
```
