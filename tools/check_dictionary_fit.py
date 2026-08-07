#!/usr/bin/env python3
"""Check that a language dictionary is complete and fits both releases."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def source_count(path: Path) -> int:
    return sum(
        1
        for line in path.read_text(encoding="ascii").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )


def check_modes(lengths: dict[str, int], release: str) -> None:
    modes = {
        "short (3-4)": range(3, 5),
        "medium (5-7)": range(5, 8),
        "long (8-15)": range(8, 16),
    }
    for name, values in modes.items():
        if sum(int(lengths.get(str(length), 0)) for length in values) == 0:
            raise SystemExit(f"{release}: no words for {name} mode")


def check(
    manifest_path: Path,
    words_path: Path,
    expected_48: int,
    expected_128: int,
    max_48_bytes: int,
) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="ascii"))
    zx48 = manifest["zx48"]
    zx128 = manifest["zx128"]

    available = source_count(words_path)
    if available < expected_128:
        raise SystemExit(
            f"source list has {available} words; {expected_128} are required"
        )
    if manifest.get("source_count") != available:
        raise SystemExit(
            f"manifest source count {manifest.get('source_count')} != {available}"
        )
    if zx48["words"] != expected_48:
        raise SystemExit(f"48K contains {zx48['words']} words, expected {expected_48}")
    if zx128["words"] != expected_128:
        raise SystemExit(
            f"128K contains {zx128['words']} words, expected {expected_128}"
        )
    if zx48["bytes"] > max_48_bytes or not zx48.get("fits"):
        raise SystemExit(
            f"48K dictionary uses {zx48['bytes']} / {max_48_bytes} bytes"
        )

    banks = zx128.get("banks", [])
    if len(banks) != 5:
        raise SystemExit(f"128K contains {len(banks)} dictionary banks, expected 5")
    for bank in banks:
        if bank["bytes"] > 16_384:
            raise SystemExit(
                f"128K bank {bank['physical_bank']} uses {bank['bytes']} / 16384 bytes"
            )
    if sum(int(bank["words"]) for bank in banks) != expected_128:
        raise SystemExit("128K bank word counts do not add up")
    if not zx128.get("fits"):
        raise SystemExit("128K dictionary manifest reports an overflow")

    check_modes(zx48["lengths"], "48K")
    check_modes(zx128["lengths"], "128K")
    print(
        f"PASS {manifest.get('language', '?')}: "
        f"48K {zx48['words']} words/{zx48['bytes']} bytes; "
        f"128K {zx128['words']} words/{zx128['bytes']} bytes in 5 banks"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--words", type=Path, required=True)
    parser.add_argument("--expected-48", type=int, required=True)
    parser.add_argument("--expected-128", type=int, required=True)
    parser.add_argument("--max-48-bytes", type=int, required=True)
    args = parser.parse_args()
    check(
        args.manifest,
        args.words,
        args.expected_48,
        args.expected_128,
        args.max_48_bytes,
    )


if __name__ == "__main__":
    main()
