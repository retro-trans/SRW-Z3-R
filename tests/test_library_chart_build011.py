"""Source-backed Library animation, chart boundaries and actual lookup path."""
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_game import Build
from cpk import CPK
from rengoku_runtime import DEFAULT_FONT
import rengoku_title_art as T
import rengoku_library_chart as L
from test_screenshot_runtime import Machine


class LibraryChart011(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT / 'work/pkg').exists(): raise unittest.SkipTest('Local source assets unavailable')
        cls.b = Build(DEFAULT_FONT)
        cls.base = T.apply(cls.b.asset('work/pkg/' + L.EFF + ':133'))
        cls.out, cls.report = L.prepare(cls.b.asset, cls.base)
        cls.hooks, cls.titles = L.chapter_hooks(cls.b.codec, cls.b.occ.values(), cls.b.original_elf)

    def test_own_rengoku_resource_bindings_and_all_menu_states(self):
        c = CPK(str(ROOT / 'work/pkg/USRDIR/COMMONDATA_REN/KURODATA/LUACPKZ3REN.CPK'))
        raw = c.read(next(e for e in c.files if e['id'] == 1))
        self.assertIn(b'ScAnime_Z3_CHART_01_2D              = 130', raw)
        self.assertIn(b'ScAnime_Z3_CHART_02_2D              = 131', raw)
        self.assertIn(b'ScAnime_Z3TITLE_MENU_2D             = 133', raw)
        self.assertEqual(self.report['menu_animation_samples'], 5360)
        self.assertEqual(len(self.report['menu_labels']), 5)

    def test_menu_composes_with_title_and_preserves_all_other_bytes(self):
        built = self.out[(L.EFF, 133)]
        L.verify_regions(self.base, built, T.GTF, [(5, r) for r, *_ in L.MENU])
        self.assertEqual(T.atlas(self.base).tobytes(), T.atlas(built).tobytes())
        bad = bytearray(built); bad[100] ^= 1
        with self.assertRaises(ValueError):
            L.verify_regions(self.base, bytes(bad), T.GTF, [(5, r) for r, *_ in L.MENU])

    def test_chart_controls_nodes_and_every_animation_byte_preserved(self):
        for mid, (gtf, _) in L.CHARTS.items():
            raw = self.b.asset('work/pkg/' + L.EFF + ':' + str(mid)); built = self.out[(L.EFF, mid)]
            self.assertEqual(raw[:gtf], built[:gtf])
            regions = [(1, L.HEADER)] + ([(2, (0, 0, 1280, 720))] if mid == 131 else [])
            L.verify_regions(raw, built, gtf, regions)
            before, after = L.atlas(raw, gtf, 1), L.atlas(built, gtf, 1)
            for box in ((640, 0, 1280, 128), (0, 128, 1280, 720)):
                self.assertEqual(before.crop(box).tobytes(), after.crop(box).tobytes())

    def test_all_chapter_wrappers_and_episode_prefixes_use_converted_lookup(self):
        self.assertEqual(len(self.hooks), 115)
        self.assertEqual(len(self.titles), 15)
        for source, target in self.hooks.items():
            m = Machine(self.b.codec, self.hooks)
            m.put(m.state + 0xb8, source + b'\0')
            self.assertEqual(m.run('converted', b'ignored'), 0x141a0)
            self.assertEqual(m.cstr(m.r[31]), target)
        self.assertEqual(self.hooks['『翠の地球』'.encode('cp932')], self.b.codec.encode('Green Earth'))
        self.assertEqual(self.hooks['第１４話'.encode('cp932')], self.b.codec.encode('Episode 14'))
        self.assertNotIn('翠の地球へ行く'.encode('cp932'), self.hooks)

    def test_native_chart_width_height_and_longest_title_bounds(self):
        raw = self.b.original_elf
        self.assertEqual(raw[0x1b8bf0 - 0x10000:0x1b8bf8 - 0x10000], bytes.fromhex('3900002439200028'))
        self.assertEqual(struct.unpack_from('>f', raw, 0x953f88 - 0x48c0 - 0x10000)[0], 214.0)
        self.assertLess(max(r['width_at_36px'] for r in self.titles), 800)

    def test_wrong_original_rejected(self):
        raw = bytearray(self.b.asset('work/pkg/' + L.EFF + ':131')); raw[0] ^= 1
        with self.assertRaises(ValueError): L.chart_apply(bytes(raw), 131)


if __name__ == '__main__': unittest.main()
