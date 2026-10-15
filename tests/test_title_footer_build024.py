"""Guard Rengoku's packed footer and successful-build numbering."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from cpk import CPK
from rengoku_runtime import DEFAULT_FONT
import build_version as V
import rengoku_title_art as T
import rengoku_library_chart as L
import rengoku_title_footer as F


class Footer024(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT/'work/pkg').exists():
            raise unittest.SkipTest('Local original assets unavailable')
        c = CPK(str(ROOT/'work/pkg'/T.EFF))
        cls.raw = c.read(next(e for e in c.files if e['id'] == T.MEMBER))
        animation = c.read(next(e for e in c.files if e['id'] == 134))
        cls.base = L.menu_apply(cls.raw, animation, T.apply(cls.raw))
        cls.built = F.apply(cls.raw, cls.base, DEFAULT_FONT, '0.1.3')

    def test_title_library_native_z_and_other_backgrounds_survive(self):
        self.assertEqual(F.restore(self.raw, self.built), self.base)
        self.assertEqual(self.raw[:T.GTF], self.built[:T.GTF])
        self.assertEqual(T.atlas(self.built).tobytes(), T.atlas(self.base).tobytes())
        self.assertEqual(L.atlas(self.built,T.GTF,5).tobytes(), L.atlas(self.base,T.GTF,5).tobytes())
        for texture in (2,3,4,6,7,8):
            self.assertEqual(L.atlas(self.raw,T.GTF,texture).tobytes(), L.atlas(self.built,T.GTF,texture).tobytes())
        self.assertTrue(F.verify(self.raw,self.built,DEFAULT_FONT,'0.1.3')['verified'])

    def test_old_version_or_missing_footer_cannot_pass(self):
        for built, version in ((self.base,'0.1.3'), (self.built,'0.1.4')):
            with self.assertRaises(ValueError):
                F.verify(self.raw,built,DEFAULT_FONT,version)
        with self.assertRaises(ValueError):
            F.apply(self.raw,self.built,DEFAULT_FONT,'0.1.4')

    def test_source_drift_or_changes_outside_footer_are_rejected(self):
        bad=bytearray(self.built);bad[100]^=1
        with self.assertRaises(ValueError):
            F.verify(self.raw,bytes(bad),DEFAULT_FONT,'0.1.3')
        bad=bytearray(self.raw);bad[F.texture_span(self.raw)[0]+128]^=1
        with self.assertRaises(ValueError):
            F.apply(bytes(bad),self.base,DEFAULT_FONT,'0.1.3')


class Version024(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/'build_version.json').write_text('{"last_successful_build":"0.1.2"}',encoding='utf8')
        self.out=self.root/'build';self.out.mkdir()
        self.report=dict(version='0.1.3',title_footer_version='0.1.3',pending=[],
            archive_readback_verified=True,sdat_roundtrip_verified=True,source_files_preserved=True,
            catalogs_preserved=True,game_files={'file':{'sha256':'test'}},patch_zip={'sha256':'test'},
            title_footer={'verified':True,'credit':F.CREDIT})

    def test_preview_and_failed_builds_do_not_consume_number(self):
        self.assertEqual(V.next_version(self.root),'0.1.3')
        self.assertEqual(V.next_version(self.root),'0.1.3')
        for key in ('archive_readback_verified','source_files_preserved','catalogs_preserved'):
            report=copy.deepcopy(self.report);report[key]=False
            with self.assertRaises(ValueError):V.stamp(self.out,report,'0.1.3',self.root)
            self.assertEqual(V.next_version(self.root),'0.1.3')
        self.assertFalse((self.out/'build_manifest.json').exists())

    def test_complete_build_increments_and_stamp_matches_title(self):
        V.stamp(self.out,self.report,'0.1.3',self.root)
        self.assertEqual(V.next_version(self.root),'0.1.4')
        m=json.loads((self.out/'build_manifest.json').read_text())
        self.assertEqual(m['version'],m['title_footer_version'])
        self.assertEqual(m['title_footer_credit'],F.CREDIT)
        self.assertFalse((self.root/'build_version.lock').exists())

    def test_stale_version_mismatched_footer_and_concurrent_build_are_rejected(self):
        with self.assertRaises(ValueError):V.next_version(self.root,'0.1.2')
        report=copy.deepcopy(self.report);report['title_footer_version']='0.1.2'
        with self.assertRaises(ValueError):V.stamp(self.out,report,'0.1.3',self.root)
        (self.root/'build_version.json').write_text('{"last_successful_build":"0.1.3"}')
        with self.assertRaises(ValueError):V.stamp(self.out,self.report,'0.1.3',self.root)
        self.assertFalse((self.out/'build_manifest.json').exists())
        self.assertFalse((self.root/'build_version.lock').exists())


if __name__ == '__main__':
    unittest.main()
