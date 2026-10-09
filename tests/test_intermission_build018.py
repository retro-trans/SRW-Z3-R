"""Actual Rengoku fields, panel clearances and isolated heading sprite."""
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_game import Build
from cpk import CPK
from inspect_artwork import textures
from rengoku_runtime import DEFAULT_FONT
from rengoku_search_layout import FSSA_ASSET, field
from rengoku_screenshot_layout import line_width
from rengoku_roster_settings_layout import x
import rengoku_intermission_layout as L


class Intermission018(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT / 'work/pkg').exists():
            raise unittest.SkipTest('Original local assets unavailable')
        cls.build = Build(DEFAULT_FONT)
        cls.source = cls.build.asset(FSSA_ASSET)
        cls.out = cls.build.fssa(cls.source, cls.build.byasset[FSSA_ASSET])
        cls.codec = cls.build.codec

    def test_joined_titles_and_pp_rows_keep_native_spacing_and_values(self):
        for row, (_, en) in L.LABELS.items():
            self.assertEqual(field(self.out, row), self.codec.encode(en))
        for row, center in L.CENTERS.items():
            en = L.LABELS[row][1]
            width = line_width(self.codec, en, 31)
            self.assertAlmostEqual(x(self.out, row) + width / 2, center, places=4)
            self.assertLess(width, 220)
            self.assertEqual(field(self.out, row + 32), b'')
        self.assertEqual(self.out[0x9e304 + 8:0x9e304 + 32],
                         self.source[0x9e304 + 8:0x9e304 + 32])
        for s in L.LABELS[0x9e304][1].split('\n'):
            self.assertLess(x(self.out, 0x9e304) + line_width(self.codec, s, 28), 220)
        # Suffix edits do not rewrite either score value or PP's live fields.
        for row in (0xa6fa4, 0xa6fc4, 0xa2ce4, 0xa2ee4):
            self.assertEqual(self.out[row:row + 32], self.source[row:row + 32])

    def test_stat_labels_clear_adjacent_headers_and_numeric_columns(self):
        for row in (0x9f084, 0xa3fc4):
            width = line_width(self.codec, 'MEL', 28)
            self.assertGreater(x(self.out, row + 32) - x(self.out, row) - width, 12)
        for row in (0x9f0e4, 0xa4024):
            self.assertGreater(x(self.out, row + 32) - x(self.out, row) -
                               line_width(self.codec, 'DEF', 28), 40)
        # Conservative boundary: the original numeric anchor, before any
        # native alignment, is 52px after MEL and 48px after DEF.
        for row in (0xa2c24, 0xa2e24):
            self.assertGreater(x(self.source, row) + 52 - x(self.out, row) -
                               line_width(self.codec, 'MEL', 25), 8)
        for row in (0x9ec24, 0x9ece4, 0xa2c84, 0xa2e84):
            self.assertGreater(x(self.source, row) + 48 - x(self.out, row) -
                               line_width(self.codec, 'DEF', 25), 7)
        self.assertLess(line_width(self.codec, 'MEL', 36), 80)
        self.assertLess(line_width(self.codec, 'DEF', 36), 80)

    def test_complete_menu_words_use_native_whole_caption_centering(self):
        for row, template in L.MENU_STYLES.items():
            for a, b in ((4, 12), (16, 24)):
                self.assertEqual(self.out[row + a:row + b], self.source[template + a:template + b])
            self.assertEqual(self.out[row + 12:row + 16], self.source[row + 12:row + 16])
            self.assertLess(line_width(self.codec, L.LABELS[row][1], self.out[row + 19]), 225)
        self.assertLess(line_width(self.codec, 'Parts', 31), 100)

    def test_only_intermission_word_cell_changes_in_swizzled_atlas(self):
        raw = self.build.asset('work/pkg/' + L.AID + ':1')
        out = L.apply_art(raw)
        self.assertEqual(len(raw), len(out))
        before = next(textures(raw))[2]
        after = next(textures(out))[2]
        self.assertEqual(after.crop((0, 192, 296, 232)).tobytes(), L.header_tile().tobytes())
        restored = after.copy()
        restored.paste(before.crop((0, 192, 296, 232)), (0, 192))
        self.assertEqual(restored.tobytes(), before.tobytes())
        self.assertEqual(raw[256 + 512 * 512 * 4:], out[256 + 512 * 512 * 4:])
        self.assertTrue(L.header_tile().getbbox()[2] <= 292)
        with self.assertRaises(ValueError):
            L.apply_art(bytes([raw[0] ^ 1]) + raw[1:])


if __name__ == '__main__':
    unittest.main()
