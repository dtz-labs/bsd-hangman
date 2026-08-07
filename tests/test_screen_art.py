import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCREEN_SOURCE = (ROOT / "src" / "screen.c").read_text(encoding="ascii")


class BsdScreenArtTests(unittest.TestCase):
    def test_noose_is_the_original_bsd_art(self):
        expected = [
            "     ______",
            "     |    |",
            "     |",
            "     |",
            "     |",
            "     |",
            "   __|_____",
            "   |      |___",
            "   |_________|",
        ]
        body = SCREEN_SOURCE[
            SCREEN_SOURCE.index("static void draw_noose(void)") :
            SCREEN_SOURCE.index("void screen_draw_error_part")
        ]
        self.assertEqual(re.findall(r'"([ _|]+)"', body), expected)

    def test_error_parts_use_the_original_bsd_sequence(self):
        expected = [
            (10, 2, "O"),
            (10, 3, "|"),
            (10, 4, "|"),
            (9, 5, "/"),
            (9, 3, "/"),
            (11, 3, "\\"),
            (11, 5, "\\"),
        ]
        body = SCREEN_SOURCE[
            SCREEN_SOURCE.index("void screen_draw_error_part") :
            SCREEN_SOURCE.index("void screen_draw_gallows")
        ]
        parts = re.findall(
            r"GALLOWS_COLUMN \+ (\d+)u\).*?"
            r"GALLOWS_ROW \+ (\d+)u\), '((?:\\\\)|.)', UI_GALLOWS",
            body,
            re.DOTALL,
        )
        actual = [
            (int(column), int(row), "\\" if char == "\\\\" else char)
            for column, row, char in parts
        ]
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
