"""Source-backed search/ally-list bounds and Effect hook regressions."""
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_game import Build
import rengoku_runtime as R
import rengoku_search_layout as S
from rengoku_screenshot_layout import line_width
from test_screenshot_runtime import Machine


class Layout007(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT / 'work/pkg').exists():
            raise unittest.SkipTest('Original local assets unavailable')
        cls.build = Build(R.DEFAULT_FONT)
        cls.raw = cls.build.asset(S.FSSA_ASSET)
        cls.out = cls.build.fssa(cls.raw, cls.build.byasset[S.FSSA_ASSET])
        cls.rpw = cls.build.asset(S.RPW_ASSET)
        cls.hooks, cls.proof = S.effect_hooks(cls.rpw, cls.build.byasset[S.RPW_ASSET], cls.build.codec)

    def x(self, row):
        return 640 + struct.unpack_from('>f', self.out, row + 4)[0] * 640

    def width(self, row, text):
        return line_width(self.build.codec, text, self.out[row + 19])

    def test_search_tabs_fit_both_selected_and_inactive_styles(self):
        # Measured tab interiors are 220px. The original selected heading
        # was 258.66px; compact labels retain the original glow/style flags.
        for row, label in ((0x96f24, 'Spirits'), (0x97104, 'Spirits'),
                           (0x96f64, 'Abilities'), (0x97144, 'Abilities')):
            self.assertEqual(S.field(self.out, row), self.build.codec.encode(label))
            self.assertLess(self.width(row, label), 220)
            self.assertEqual(self.out[row + 4:row + 32], self.raw[row + 4:row + 32])
        self.assertEqual(self.out[0x96f24 + 18], 160)  # encoded glow, not font height
        for row in (0x96fa4, 0x97024, 0x970a4):
            self.assertEqual(S.field(self.out, row), self.build.codec.encode('Spirits'))
            self.assertLess(self.width(row, 'Spirits'), 120)

    def test_split_sp_cost_heading_keeps_value_column_and_spacing(self):
        self.assertEqual(S.field(self.out, 0x9d3e4), self.build.codec.encode('SP Cost\n'))
        self.assertEqual(S.field(self.out, 0x9d404), b'')
        self.assertEqual(S.field(self.out, 0x9d424), 'ＳＰ'.encode('cp932'))
        self.assertEqual(S.field(self.out, 0x9d424), S.field(self.raw, 0x9d424))
        self.assertLess(self.x(0x9d3e4) + self.width(0x9d3e4, 'SP Cost') + 12,
                        self.x(0x9d424))
        for row in (0x9d3e4, 0x9d404, 0x9d424):
            self.assertEqual(self.out[row + 4:row + 32], self.raw[row + 4:row + 32])

    def test_ally_columns_fit_all_copies_and_leave_focus_value_room(self):
        for first in (0x9f344, 0x9f584, 0xa3ae4, 0xa3e04):
            self.assertEqual(S.field(self.out, first), self.build.codec.encode('Rpr.'))
            self.assertEqual(S.field(self.out, first + 32), self.build.codec.encode('Res.'))
            self.assertLess(self.x(first) + self.width(first, 'Rpr.') + 12, self.x(first + 32))
        for first in (0x9f5c4, 0xa3b24):
            self.assertEqual(S.field(self.out, first), self.build.codec.encode('Sup Atk'))
            self.assertEqual(S.field(self.out, first + 32), self.build.codec.encode('Sup Def'))
            self.assertLess(self.x(first) + self.width(first, 'Sup Atk') + 12, self.x(first + 32))
            self.assertLess(self.x(first + 32) + self.width(first + 32, 'Sup Def'), 1230)
        for row in (0x9ed84, 0xa2684):
            self.assertEqual(S.field(self.out, row), self.build.codec.encode('Foc'))
            self.assertLess(self.x(row) + self.width(row, 'Foc') + 12, 1180)
        # Width fixes must never move the rows or alter their render modes.
        for row in S.LABELS:
            self.assertEqual(self.out[row + 4:row + 32], self.raw[row + 4:row + 32])

    def test_every_spirit_and_pilot_skill_effect_fits_without_lost_words(self):
        self.assertEqual(self.proof['bindings'], 204)
        self.assertEqual(self.proof['unique_descriptions'], 187)
        families = {'spirit': 0, 'sk-pri': 0}
        for row in self.proof['rows']:
            families[row['family']] += 1
            source = self.build.occ[row['occurrence']]
            self.assertEqual(row['display'].split(), source['english'].split())
            self.assertLessEqual(len(row['display'].splitlines()), 2 if row['family'] == 'spirit' else 3)
            for line in row['display'].splitlines():
                self.assertLessEqual(line_width(self.build.codec, line, row['glyph_quad']), row['width_limit'])
        self.assertEqual(families, {'spirit': 42, 'sk-pri': 162})
        self.assertNotIn('精神耐性'.encode('cp932'), self.hooks)  # name remains a name
        expected = ('Blocks stat-halving, action-stop, Focus-down\n'
                    'and SP-down effects. Negates Daunt when\n'
                    'Focus is 100 or less. No effect for sub-pilots.')
        mind = [r for r in self.proof['rows'] if r['name'] == '精神耐性']
        self.assertEqual(len(mind), 2)
        for row in mind:
            self.assertEqual(row['display'], expected)
            jp = self.build.occ[row['occurrence']]['jp'].encode('cp932')
            for method in ('draw', 'converted'):
                m = Machine(self.build.codec, self.hooks)
                if method == 'converted':
                    m.put(m.state + 0xb8, jp + b'\0')
                m.run(method, jp)
                actual = m.cstr(m.r[31 if method == 'converted' else 3])
                self.assertEqual(actual, self.build.codec.encode(expected))
                self.assertEqual(actual.count(b'\n'), 2)

    def test_source_guards_and_oversize_descriptions_fail_closed(self):
        bad = bytearray(self.rpw)
        bad[100] ^= 1
        with self.assertRaises(ValueError):
            S.effect_hooks(bad, self.build.byasset[S.RPW_ASSET], self.build.codec)
        bad = bytearray(self.raw)
        bad[0x9d404:0x9d408] = bad[0x9d3e4:0x9d3e8]
        with self.assertRaises(ValueError):
            S.apply_fssa(bad, self.out, self.build.codec)
        with self.assertRaises(ValueError):
            S.wrap_effect(self.build.codec, 'word ' * 500, 3)


if __name__ == '__main__':
    unittest.main()
