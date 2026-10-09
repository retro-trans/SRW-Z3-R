"""Title sprites in both native layouts, with byte-exact animation protection."""
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from cpk import CPK
import rengoku_title_art as T


class Title010(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT / 'work/pkg').exists():
            raise unittest.SkipTest('Original local assets unavailable')
        c = CPK(str(ROOT / 'work/pkg' / T.EFF))
        cls.raw = c.read(next(e for e in c.files if e['id'] == T.MEMBER))
        cls.built = T.apply(cls.raw)

    def test_own_game_title_constant_and_all_animation_samples(self):
        c = CPK(str(ROOT / 'work/pkg/USRDIR/COMMONDATA_REN/KURODATA/LUACPKZ3REN.CPK'))
        raw = c.read(next(e for e in c.files if e['id'] == 1))
        self.assertIn(b'ScAnime_Z3TITLE_2D                  = 132', raw)
        T.audit(self.raw)
        self.assertEqual(sum(s[-1] for s in T.SAMPLES[:2]), 3393)

    def test_every_unrelated_byte_and_all_z_frames_preserved(self):
        T.verify(self.raw, self.built)
        self.assertEqual(self.raw[:T.GTF], self.built[:T.GTF])
        before, after = T.atlas(self.raw), T.atlas(self.built)
        for box in T.Z_BOXES:
            self.assertEqual(before.crop(box).tobytes(), after.crop(box).tobytes())
        bad = bytearray(self.built); bad[0] ^= 1
        with self.assertRaises(ValueError):
            T.verify(self.raw, bytes(bad))

    def test_real_alpha_and_exact_z31_wordmark(self):
        tiles = list(T.tiles())
        for (x, y, w, h), im in tiles:
            self.assertEqual(im.mode, 'RGBA')
            self.assertEqual(im.size, (w, h))
            self.assertEqual(im.getchannel('A').getextrema(), (0, 255))
            self.assertEqual(im.getpixel((w - 1, 0))[3], 0)
        path = ROOT.parent / 'SRW Z3/work/title_logo_final/wordmark.png'
        if path.exists():
            with Image.open(path) as reference:
                self.assertEqual(tiles[0][1].tobytes(), reference.tobytes())
        alpha = tiles[1][1].getchannel('A')
        self.assertEqual(alpha.getbbox(), (8, 5, 324, 84))
        self.assertIsNone(alpha.crop((0, 85, 339, 117)).getbbox())
        for rect, tile in tiles:
            x, y, w, h = rect
            packed = T.atlas(self.built).crop((x, y, x + w, y + h))
            # Both-invisible RGB is deliberately retained from the original.
            for old, new in zip(packed.getdata(), tile.getdata()):
                if old[3] or new[3]: self.assertEqual(old, new)

    def test_large_and_menu_wordmark_subtitle_quads_exist(self):
        cases = (
            ((-435, -181, 200, -181, -435, 85, 200, 85), T.SAMPLES[0]),
            ((-153, -232, 306, -232, -153, -40, 306, -40), T.SAMPLES[0]),
            ((-251, 33, 55, 33, -251, 138, 55, 138), T.SAMPLES[1]),
            ((-19, -77, 201, -77, -19, -1, 201, -1), T.SAMPLES[1]))
        for quad, sample in cases:
            pattern = struct.pack('>8h6H', *quad, *sample[:6]) + b'\x01\x01\0\x01'
            self.assertIn(pattern, self.raw[:T.GTF])
            self.assertIn(pattern, self.built[:T.GTF])
        self.assertGreater(T.composition(self.built).width,
                           T.composition(self.built, True).width)

    def test_wrong_source_or_unreviewed_art_is_rejected(self):
        bad = bytearray(self.raw); bad[T.GTF + 8] ^= 1
        with self.assertRaises(ValueError): T.apply(bytes(bad))
        meta = T.config(); meta['subtitle']['sha256'] = '0' * 64
        with patch.object(T, 'config', return_value=meta):
            with self.assertRaises(ValueError): list(T.tiles())


if __name__ == '__main__':
    unittest.main()
