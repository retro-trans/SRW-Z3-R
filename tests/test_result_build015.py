"""Keep kill totals separate from Level; preserve the other counter settings."""
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_game import Build
from cpk import CPK
import rengoku_runtime as R
import rengoku_result_layout as L
from rengoku_search_layout import FSSA_ASSET, field
from rengoku_screenshot_layout import line_width
from rengoku_roster_settings_layout import x


class Results015(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT / 'work/pkg').exists():
            raise unittest.SkipTest('Original local assets unavailable')
        cls.build = Build(R.DEFAULT_FONT)
        cls.source = cls.build.asset(FSSA_ASSET)
        cls.out = cls.build.fssa(cls.source, cls.build.byasset[FSSA_ASSET])
        cls.codec = cls.build.codec

    def test_header_and_compact_suffix_keep_live_fields_and_pilot_suffix(self):
        for row, (_, text) in L.LABELS.items():
            self.assertEqual(field(self.out, row), self.codec.encode(text))
            self.assertEqual(self.out[row + 4:row + 32], self.source[row + 4:row + 32])
        self.assertLess(x(self.out, 0x99ce4) + line_width(self.codec, 'Kills', 28) + 12,
                        x(self.out, L.LEVEL_HEADER))
        # Both dynamic total records and the neighboring Lv label are intact.
        for row in (0xa6fa4, 0xa6fc4, L.LEVEL_HEADER):
            self.assertEqual(self.out[row:row + 32], self.source[row:row + 32])
        # Build 018 removes the shared suffix from Pilot Info/Intermission.
        self.assertEqual(field(self.out, L.PILOT_SUFFIX), b'')
        self.assertEqual(self.out[L.PILOT_SUFFIX + 18:L.PILOT_SUFFIX + 20], bytes((31, 31)))
        # Intermission's second/third counters lose their redundant suffix
        # in 018; the unrelated carryover label is still intact.
        for row in (0x99344,):
            self.assertEqual(field(self.out, row), self.codec.encode('Units'))
        # The original compact widget contains both numeric placeholders and
        # this exact suffix. The results header fragments belong to one group.
        self.assertEqual(self.source[0xe8f18:0xe8f24], bytes.fromhex('0f0410000f0510000f061000'))
        self.assertEqual(self.source[0xe4fac:0xe4fb8], bytes.fromhex('086e1000086f100008701000'))

    def test_previous_build_changes_only_three_text_pointers_and_appended_labels(self):
        path = ROOT / 'work/builds/rengoku_en_014/RPCS3/NPJB00689/USRDIR/DATA_REN/AIDDATA/AIDDATAPACK_R.CPK'
        if not path.exists():
            self.skipTest('Previous local build unavailable')
        pack = CPK(str(path))
        previous = pack.read(next(e for e in pack.files if e['id'] == 0))
        # Keep the comparison scoped to this layer as later screens evolve.
        current = L.apply_fssa(self.source, previous, self.codec)[0]
        allowed = {p for row in L.LABELS for p in range(row, row + 4)}
        self.assertTrue(all(a == b or p in allowed for p, (a, b) in enumerate(zip(previous, current))))
        self.assertEqual(len(current) - len(previous), 13)
        for row in L.LABELS:
            stale = bytearray(self.source)
            struct.pack_into('>I', stale, row, 0)
            with self.assertRaises(ValueError):
                L.apply_fssa(stale, previous, self.codec)


if __name__ == '__main__':
    unittest.main()
