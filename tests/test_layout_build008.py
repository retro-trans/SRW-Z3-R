"""Actual team-list and settings records from the two reported screens."""
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_game import Build
import rengoku_runtime as R
import rengoku_roster_settings_layout as L
from rengoku_search_layout import FSSA_ASSET, field
from rengoku_screenshot_layout import line_width


class Layout008(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT / 'work/pkg').exists():
            raise unittest.SkipTest('Original local assets unavailable')
        cls.build = Build(R.DEFAULT_FONT)
        cls.raw = cls.build.asset(FSSA_ASSET)
        cls.out = cls.build.fssa(cls.raw, cls.build.byasset[FSSA_ASSET])

    def test_all_eight_settings_states_fit_and_keep_original_style(self):
        self.assertEqual(len(L.TABS), 8)
        for i, row in enumerate(range(0x96e24, 0x96f24, 32)):
            label = 'Settings ' + str(1 + i % 2)
            self.assertEqual(field(self.out, row), self.build.codec.encode(label))
            self.assertEqual(self.out[row + 4:row + 32], self.raw[row + 4:row + 32])
            self.assertAlmostEqual(L.x(self.out, row), (233.5, 505.5)[i % 2], places=4)
            self.assertLess(line_width(self.build.codec, label, 31), 210)

    def test_narrow_support_pairs_fit_while_retaining_their_centers(self):
        for row, (_, en) in L.SUPPORT.items():
            self.assertEqual(field(self.out, row), self.build.codec.encode(en))
            self.assertEqual(self.out[row + 16:row + 22], bytes((21, 21, 19, 21, 21, 21)))
            self.assertEqual(self.out[row + 8:row + 16], self.raw[row + 8:row + 16])
            self.assertEqual(self.out[row + 22:row + 32], self.raw[row + 22:row + 32])
            width = line_width(self.build.codec, en, 21)
            self.assertAlmostEqual(L.x(self.out, row) + width / 2,
                                   L.x(self.raw, row) + 28, places=4)
        for attack, defense in ((0x9f884, 0x9f8a4), (0xa35e4, 0xa3604), (0xa4584, 0xa45a4)):
            attack_end = L.x(self.out, attack) + line_width(self.build.codec, 'S. Atk', 21)
            self.assertGreater(L.x(self.out, defense) - attack_end, 9)
            self.assertLess(L.x(self.out, defense) + line_width(self.build.codec, 'S. Def', 21), 1230)

    def test_move_footer_components_shift_together_and_fit_strip(self):
        for row in (0xa29a4, 0xa29c4, 0xa29e4):
            self.assertAlmostEqual(L.x(self.out, row) - L.x(self.raw, row), 32, places=4)
            self.assertEqual(self.out[row + 8:row + 32], self.raw[row + 8:row + 32])
        for row in (0x9eea4, 0xa2984):
            self.assertEqual(field(self.out, row), self.build.codec.encode('Move'))
            self.assertEqual(self.out[row + 4:row + 32], self.raw[row + 4:row + 32])
            self.assertAlmostEqual(L.x(self.out, 0xa29a4) - L.x(self.out, row)
                                   - line_width(self.build.codec, 'Move', 24), 10, places=4)
        # Bracket's last glyph stays inside the 640px strip. Numbers, slash,
        # and four terrain cells retain their offsets inside the bracket.
        self.assertLess(L.x(self.out, 0xa29a4) + 176 + 25, 640)
        self.assertAlmostEqual(L.x(self.out, 0xa29e4) - L.x(self.out, 0xa29a4), 23, places=4)
        self.assertAlmostEqual(L.x(self.out, 0xa29c4) - L.x(self.out, 0xa29a4), 75, places=4)

    def test_unrelated_rows_and_bad_sources(self):
        # Apply only the new layer to pristine bytes to audit every change;
        # broader English insertion is checked by the build/readback pipeline.
        out, report = L.apply_fssa(self.raw, self.raw, self.build.codec)
        allowed = set()
        for row in L.TABS:
            allowed.update(range(row, row + 4))
        for row in L.SUPPORT:
            allowed.update(range(row, row + 8))
            allowed.update(range(row + 16, row + 22))
        for row in L.FOOTER:
            allowed.update(range(row + 4, row + 8))
        self.assertEqual(len(report), 17)
        self.assertTrue(all(a == b or p in allowed for p, (a, b) in enumerate(zip(self.raw, out))))
        # A unit-view support heading must retain its separate larger style.
        self.assertEqual(out[0x9f5c4:0x9f604], self.raw[0x9f5c4:0x9f604])
        bad = bytearray(self.raw)
        bad[0x9f884 + 20] = 27
        with self.assertRaises(ValueError):
            L.apply_fssa(bad, bad, self.build.codec)
        bad = bytearray(self.raw)
        bad[0xa29a4 + 20] = 175
        with self.assertRaises(ValueError):
            L.apply_fssa(bad, bad, self.build.codec)


if __name__ == '__main__':
    unittest.main()
