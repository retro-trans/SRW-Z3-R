"""Source-bound battle-preview widths, fragments and unrelated-byte guards."""
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_game import Build
from cpk import CPK
import rengoku_runtime as R
import rengoku_battle_preview_layout as L
from rengoku_search_layout import FSSA_ASSET, field
from rengoku_roster_settings_layout import x
from rengoku_screenshot_layout import line_width


class BattlePreview013(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT / 'work/pkg').exists():
            raise unittest.SkipTest('Original local assets unavailable')
        cls.build = Build(R.DEFAULT_FONT)
        cls.raw = cls.build.asset(FSSA_ASSET)
        cls.styles = cls.build.asset(L.STYLE_ASSET)
        cls.out = cls.build.fssa(cls.raw, cls.build.byasset[FSSA_ASSET])
        cls.codec = cls.build.codec

    def test_real_presets_reproduce_reported_overflows(self):
        # Actual preset dimensions, not the row's 24px/25px pitch bytes.
        for row, old, quad, available in (
                (0xa0444, 'Attack', 37, 94),
                (0xa70e4, 'Ammo Remaining', 23, 57),
                (0xa03e4, 'Focus', 25, 56),
                (0xa0424, 'Focus', 25, 56)):
            preset = self.raw[row + 22] & 15
            self.assertEqual(struct.unpack_from('>h', self.styles, 0x488 + 16 * preset)[0], quad)
            self.assertGreater(line_width(self.codec, old, quad), available)
        # Two individually translated cost fragments collide with the colon.
        self.assertGreater(x(self.raw, 0xa7184) + line_width(self.codec, 'Use', 23),
                           x(self.raw, 0xa71a4))
        self.assertAlmostEqual(x(self.raw, 0xa7104) - x(self.raw, 0xa70e4), 57, places=4)

    def test_all_shared_captions_fit_and_keep_full_size(self):
        self.assertEqual(len(self.build.battle_preview_report), 15)
        for row, (_, label) in L.LABELS.items():
            self.assertEqual(field(self.out, row), self.codec.encode(label))
            # No shrink, position, color, alignment, animation or counter edit.
            self.assertEqual(self.out[row + 4:row + 32], self.raw[row + 4:row + 32])
        for row in L.ACTION_ROWS:
            self.assertLessEqual(line_width(self.codec, L.LABELS[row][1], 37) + 8, 94)
        for row in L.SUPPORT_ROWS:
            self.assertLessEqual(line_width(self.codec, L.LABELS[row][1], 23) + 12, 96)
        for row in L.FOCUS_ROWS:
            self.assertLessEqual(line_width(self.codec, 'Foc', 25) + 8, 56)
        # Also check unmodified choices sharing the same large action badge.
        for row, text in ((0xa0584, 'Ctr.'), (0xa05a4, 'EVD'), (0xa0644, 'Wait')):
            self.assertEqual(field(self.out, row), self.codec.encode(text))
            self.assertLessEqual(line_width(self.codec, text, 37) + 8, 94)

    def test_weapon_variants_clear_native_colons_and_redundant_fragments(self):
        for row, label in ((0xa70e4, 'Rnd.'), (0xa7144, 'Charges'),
                           (0xa7164, 'EN'), (0xa71c4, 'S.EN')):
            colon = L.COLONS[row]
            self.assertEqual(field(self.out, row), self.codec.encode(label))
            self.assertEqual(self.out[colon:colon + 32], self.raw[colon:colon + 32])
            self.assertLessEqual(x(self.out, row) + line_width(self.codec, label, 23) + 4,
                                 x(self.out, colon))
        for row in (0xa7184, 0xa71e4, 0xa7224):
            self.assertEqual(field(self.out, row), b'')

    def test_reject_stale_source_and_preserve_every_other_build012_byte(self):
        for row in L.LABELS:
            bad = bytearray(self.raw)
            bad[row + 22] ^= 1
            with self.assertRaises(ValueError):
                L.apply_fssa(bad, self.out, self.codec, self.styles)
        bad = bytearray(self.styles)
        struct.pack_into('>h', bad, 0x488 + 4 * 16, 24)
        with self.assertRaises(ValueError):
            L.apply_fssa(self.raw, self.out, self.codec, bad)
        path = ROOT / 'work/builds/rengoku_en_012/RPCS3/NPJB00689/USRDIR/DATA_REN/AIDDATA/AIDDATAPACK_R.CPK'
        if not path.exists():
            self.skipTest('Previous local build unavailable for byte comparison')
        pack = CPK(str(path))
        previous = pack.read(next(e for e in pack.files if e['id'] == 0))
        # Compare this layer alone; later screen fixes may also edit FSSA.
        current = L.apply_fssa(self.raw, previous, self.codec, self.styles)[0]
        allowed = {p for row in L.LABELS for p in range(row, row + 4)}
        self.assertTrue(all(a == b or p in allowed for p, (a, b) in enumerate(zip(previous, current))))
        self.assertEqual(len(current) - len(previous),
                         sum(len(self.codec.encode(label)) + 1 for _, label in L.LABELS.values()))


if __name__ == '__main__':
    unittest.main()
