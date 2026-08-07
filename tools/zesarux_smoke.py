#!/usr/bin/env python3
"""Boot a Hangman TAP and exercise its menu, licence, sound, and redraws."""

from __future__ import annotations

import argparse
import json
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

PROMPT = b"command> "
SYMBOL_RE = re.compile(r"^(\S+)\s*=\s*\$([0-9A-Fa-f]+)\b", re.MULTILINE)


def receive_prompt(sock: socket.socket, timeout: float = 3.0) -> str:
    deadline = time.monotonic() + timeout
    response = bytearray()
    while not response.endswith(PROMPT):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError(f"ZRCP prompt timeout: {response!r}")
        sock.settimeout(remaining)
        chunk = sock.recv(4096)
        if not chunk:
            raise RuntimeError("ZEsarUX closed ZRCP")
        response.extend(chunk)
    return response.decode("latin-1", "replace")


def command(sock: socket.socket, text: str, timeout: float = 3.0) -> str:
    sock.sendall((text + "\n").encode("latin-1"))
    return receive_prompt(sock, timeout)


def send_physical_key(sock: socket.socket, key: int) -> None:
    command(sock, f"send-keys-event {key} 1")
    time.sleep(0.2)
    command(sock, f"send-keys-event {key} 0")


def send_key_until_byte_changes(
    sock: socket.socket,
    key: int,
    address: int,
    previous: int,
    timeout: float,
) -> int:
    """Retry a ZRCP key event if the emulated keyboard misses its first scan."""
    deadline = time.monotonic() + timeout
    last_error: RuntimeError | None = None
    while time.monotonic() < deadline:
        send_physical_key(sock, key)
        remaining = deadline - time.monotonic()
        try:
            return wait_byte_change(sock, address, previous, min(1.0, remaining))
        except RuntimeError as error:
            last_error = error
            time.sleep(0.1)
    raise RuntimeError(f"key {key} was not accepted: {last_error}")


def send_key_until_ocr(
    sock: socket.socket, key: int, needle: str, timeout: float
) -> str:
    deadline = time.monotonic() + timeout
    last_error: RuntimeError | None = None
    while time.monotonic() < deadline:
        send_physical_key(sock, key)
        try:
            return wait_ocr(sock, needle, min(1.0, deadline - time.monotonic()))
        except RuntimeError as error:
            last_error = error
    raise RuntimeError(f"key {key} did not reveal {needle!r}: {last_error}")


def assert_black_border_shadow(sock: socket.socket) -> None:
    bordcr = read_byte(sock, 0x5C48)
    if bordcr & 0x38:
        raise RuntimeError(f"ROM border shadow is not black: ${bordcr:02x}")


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def connect(proc: subprocess.Popen[bytes], port: int, timeout: float) -> socket.socket:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"ZEsarUX exited with status {proc.returncode}")
        try:
            sock = socket.create_connection(("127.0.0.1", port), timeout=0.5)
            receive_prompt(sock)
            return sock
        except OSError:
            time.sleep(0.1)
    raise RuntimeError("could not connect to ZEsarUX")


def read_byte(sock: socket.socket, address: int) -> int:
    response = command(sock, f"read-memory {address} 1")
    for line in response.splitlines():
        if re.fullmatch(r"[0-9A-Fa-f]{2}", line.strip()):
            return int(line.strip(), 16)
    raise RuntimeError(f"cannot read ${address:04x}: {response!r}")


def wait_byte(sock: socket.socket, address: int, expected: int, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        last = read_byte(sock, address)
        if last == expected:
            return
        time.sleep(0.05)
    raise RuntimeError(
        f"${address:04x} did not become ${expected:02x}; last={last!r}"
    )


def wait_byte_change(
    sock: socket.socket, address: int, previous: int, timeout: float
) -> int:
    deadline = time.monotonic() + timeout
    last = previous
    while time.monotonic() < deadline:
        last = read_byte(sock, address)
        if last != previous:
            return last
        time.sleep(0.05)
    raise RuntimeError(f"${address:04x} remained ${last:02x}")


def wait_byte_stable(
    sock: socket.socket, address: int, stable_for: float, timeout: float
) -> int:
    deadline = time.monotonic() + timeout
    last = read_byte(sock, address)
    stable_since = time.monotonic()
    while time.monotonic() < deadline:
        time.sleep(0.05)
        current = read_byte(sock, address)
        if current != last:
            last = current
            stable_since = time.monotonic()
        elif time.monotonic() - stable_since >= stable_for:
            return current
    raise RuntimeError(f"${address:04x} did not stabilize")


def wait_ocr(sock: socket.socket, needle: str, timeout: float) -> str:
    deadline = time.monotonic() + timeout
    last = ""
    while time.monotonic() < deadline:
        last = command(sock, "get-ocr")
        if needle in last:
            return last
        time.sleep(0.1)
    raise RuntimeError(f"OCR did not contain {needle!r}: {last!r}")


def symbols(path: Path) -> dict[str, int]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return {name: int(value, 16) for name, value in SYMBOL_RE.findall(text)}


def symbol(table: dict[str, int], name: str) -> int:
    for candidate in (name, f"_{name}"):
        if candidate in table:
            return table[candidate]
    raise RuntimeError(f"missing symbol {name}")


def validate_pbm(path: Path) -> None:
    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline and not path.exists():
        time.sleep(0.05)
    data = path.read_bytes()
    if not data.startswith(b"P4\n256 192\n") or len(data) < 6155:
        raise RuntimeError(f"bad screenshot: {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--machine", choices=("48k", "128k"), required=True)
    parser.add_argument("--tap", type=Path, required=True)
    parser.add_argument("--map", type=Path, required=True, dest="map_path")
    parser.add_argument("--locale-manifest", type=Path, required=True)
    parser.add_argument("--screenshot", type=Path, required=True)
    parser.add_argument(
        "--zesarux",
        type=Path,
        default=Path("/Applications/ZEsarUX.app/Contents/MacOS/zesarux"),
    )
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    locale = json.loads(args.locale_manifest.read_text(encoding="ascii"))["strings"]
    title = locale["title_48" if args.machine == "48k" else "title_128"]

    table = symbols(args.map_path)
    stage = symbol(table, "zx_boot_stage")
    length = symbol(table, "zx_selected_word_length")
    renders = symbol(table, "zx_render_count")
    redraw_rows = symbol(table, "zx_last_redraw_rows")
    full_renders = symbol(table, "zx_full_render_count")
    last_sound = symbol(table, "zx_last_sound")
    hit_letter = symbol(table, "zx_known_hit_letter")
    miss_letter = symbol(table, "zx_known_miss_letter")
    markers = (
        stage,
        length,
        renders,
        redraw_rows,
        full_renders,
        last_sound,
        hit_letter,
        miss_letter,
    )
    if args.machine == "128k" and any(address >= 0xC000 for address in markers):
        raise RuntimeError("smoke markers are not in fixed RAM")

    port = free_port()
    args.screenshot.unlink(missing_ok=True)
    emulator = [
        str(args.zesarux.resolve()),
        "--noconfigfile",
        "--machine",
        args.machine,
        "--tape",
        str(args.tap.resolve()),
        "--vo",
        "null",
        "--ao",
        "null",
        "--nosplash",
        "--enable-remoteprotocol",
        "--remoteprotocol-port",
        str(port),
        "--quickexit",
        "--fastautoload",
    ]
    proc = subprocess.Popen(emulator, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    sock: socket.socket | None = None
    clean = False
    try:
        sock = connect(proc, port, min(args.timeout, 10.0))
        wait_byte(sock, stage, 0x4D, args.timeout)
        wait_ocr(sock, title, 5.0)
        wait_ocr(sock, locale["ascii_notice"], 5.0)
        wait_ocr(sock, locale["license_key"], 5.0)
        print(f"PASS {args.machine}: no-accents notice and licence key rendered")

        send_key_until_ocr(sock, ord("l"), "ORIGINAL BSD HANGMAN", 5.0)
        wait_ocr(sock, "Michal Pasternak", 5.0)
        send_key_until_ocr(sock, ord(" "), "Redistribution and use", 5.0)
        send_key_until_ocr(sock, ord(" "), "University nor the names", 5.0)
        send_key_until_ocr(sock, ord(" "), "DIRECT, INDIRECT, INCIDENTAL", 5.0)
        send_key_until_ocr(sock, ord(" "), title, 5.0)
        wait_ocr(sock, locale["license_key"], 5.0)
        print(f"PASS {args.machine}: complete BSD licence and ZX credit rendered")

        wait_ocr(sock, locale["mode_short_line"], 5.0)
        wait_ocr(sock, locale["mode_medium_line"], 5.0)
        wait_ocr(sock, locale["mode_long_line"], 5.0)
        wait_ocr(sock, locale["mode_all_line"], 5.0)
        send_key_until_byte_changes(sock, ord("2"), stage, 0x4D, args.timeout)
        wait_byte(sock, stage, 0x47, args.timeout)
        if read_byte(sock, renders) == 0:
            wait_byte_change(sock, renders, 0, args.timeout)
        selected_length = read_byte(sock, length)
        if not 5 <= selected_length <= 7:
            raise RuntimeError(f"medium mode selected length {selected_length}")
        wait_ocr(sock, locale["guess_word"], 5.0)
        print(f"PASS {args.machine}: rendered all modes and decoded medium word")

        previous_full_renders = read_byte(sock, full_renders)
        known_hit = read_byte(sock, hit_letter)
        known_miss = read_byte(sock, miss_letter)
        if not ord("A") <= known_hit <= ord("Z"):
            raise RuntimeError(f"invalid hit letter ${known_hit:02x}")
        if not ord("A") <= known_miss <= ord("Z"):
            raise RuntimeError(f"invalid miss letter ${known_miss:02x}")

        previous_render = read_byte(sock, renders)
        send_key_until_byte_changes(
            sock, known_hit + 32, renders, previous_render, args.timeout
        )
        wait_byte_stable(sock, renders, 0.4, args.timeout)
        wait_ocr(sock, locale["letter_hit"], 5.0)
        if read_byte(sock, redraw_rows) != 3:
            raise RuntimeError("hit did not use a three-row partial update")
        if read_byte(sock, full_renders) != previous_full_renders:
            raise RuntimeError("hit caused a full-screen redraw")
        if read_byte(sock, last_sound) != 3:
            raise RuntimeError("hit did not select the rising sound")
        assert_black_border_shadow(sock)
        print(f"PASS {args.machine}: hit used partial redraw and rising sound")

        previous_render = read_byte(sock, renders)
        send_key_until_byte_changes(
            sock, known_hit + 32, renders, previous_render, args.timeout
        )
        wait_byte_stable(sock, renders, 0.4, args.timeout)
        wait_ocr(sock, locale["letter_repeat"], 5.0)
        if read_byte(sock, redraw_rows) != 1:
            raise RuntimeError("repeat updated more than its message row")
        if read_byte(sock, full_renders) != previous_full_renders:
            raise RuntimeError("repeat caused a full-screen redraw")
        if read_byte(sock, last_sound) != 1:
            raise RuntimeError("repeat did not select the repeat sound")
        assert_black_border_shadow(sock)
        print(f"PASS {args.machine}: repeat used one-row redraw and repeat sound")

        previous_render = read_byte(sock, renders)
        send_key_until_byte_changes(
            sock, known_miss + 32, renders, previous_render, args.timeout
        )
        wait_byte_stable(sock, renders, 0.4, args.timeout)
        wait_ocr(sock, locale["letter_miss"], 5.0)
        if read_byte(sock, redraw_rows) != 4:
            raise RuntimeError("miss did not use a four-row partial update")
        if read_byte(sock, full_renders) != previous_full_renders:
            raise RuntimeError("miss caused a full-screen redraw")
        if read_byte(sock, last_sound) != 2:
            raise RuntimeError("miss did not select the descending sound")
        assert_black_border_shadow(sock)
        print(f"PASS {args.machine}: miss used partial redraw and descending sound")

        command(sock, f"save-screen {args.screenshot.resolve()}")
        validate_pbm(args.screenshot)
        print(f"PASS {args.machine}: screenshot {args.screenshot}")

        sock.sendall(b"exit-emulator\n")
        sock.close()
        sock = None
        proc.wait(timeout=5.0)
        if proc.returncode != 0:
            raise RuntimeError(f"ZEsarUX exit status {proc.returncode}")
        clean = True
        return 0
    finally:
        if sock is not None:
            try:
                sock.sendall(b"exit-emulator\n")
            except OSError:
                pass
            sock.close()
        if not clean and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"smoke: ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
