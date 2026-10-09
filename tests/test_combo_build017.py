"""Execute the popup adapter and original quad-size instructions together."""
from pathlib import Path
from types import SimpleNamespace
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import rengoku_runtime as R
import rengoku_combo_runtime as C
from cpk import CPK
from test_link_runtime import CPU


class Combo017(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / 'work/eboot/EBOOT.ELF'
        if not path.exists():
            raise unittest.SkipTest('Local original assets unavailable')
        cls.source = path.read_bytes()
        cls.built, cls.report = R.patch_elf(cls.source,
            SimpleNamespace(widths={}, codes={}, unicode={}), {})

    def cpu(self, state, zoom, animation, legacy=False):
        c = CPU(self.built)
        c.put(c.r[28] + 0x30, bytes([state]))
        c.f[30], c.f[31] = zoom, animation
        c.cr = [-1, 0, 1, -1, 1, 0, 1, -1]
        if legacy:
            c.put(C.SITE, struct.pack('>I', C.ORIGINAL))
        return c

    def quad(self, c, zoom):
        # Execute the real shared drawer's zoom/half-size multiply and
        # centered quad arithmetic. The skipped words calculate only UV
        # and color. f28 is the caller's f4 copied by native 0x3a0e50.
        c.f[28] = c.f[4]
        c.r[11] = 0x2100000
        c.put(c.r[11] + 0x306c, struct.pack('>f', zoom))
        c.f[13] = 40.
        c.run(0x3a0ef0, {0x3a0ef8})
        c.run(0x3a0f24, {0x3a0f28})
        c.f[31], c.f[30] = 500., 300.
        c.run(0x3a0f30, {0x3a0f40})
        return c.f[13] - c.f[31], c.f[10] - c.f[30]

    def test_original_double_zoom_and_fixed_tile_size_across_animation(self):
        for zoom in (.25, .4, .5, .6, .75, 1., 1.25, 2.):
            for animation in (0., 1/15, .25, .5, .75, 1.):
                for legacy in (False, True):
                    c = self.cpu(C.STATE, zoom, animation, legacy)
                    c.run(C.SITE, {C.SITE + 4})
                    width, height = self.quad(c, zoom)
                    expected = (80 * zoom * zoom if legacy else 64 * zoom) * animation
                    self.assertAlmostEqual(width, expected, delta=.0002)
                    self.assertAlmostEqual(height, expected, delta=.0002)

    def test_other_states_and_live_registers_are_preserved(self):
        for state in (0, 0x33, 0x34, C.STATE, 0x36, 255):
            c = self.cpu(state, .5, .75)
            registers, floats, cr, lr = c.r[:], c.f[:], c.cr[:], c.lr
            c.writes.clear()
            c.run(C.SITE, {C.SITE + 4})
            self.assertEqual(c.r, registers)
            self.assertEqual(c.cr, cr)
            self.assertEqual(c.lr, lr)
            self.assertEqual(c.f[:4] + c.f[5:], floats[:4] + floats[5:])
            self.assertAlmostEqual(c.f[4], .6 if state == C.STATE else .375)
            self.assertLessEqual(c.writes, set(range(registers[1] - 0x50, registers[1])))

    def test_source_guard_rejects_changed_zoom_and_texture_selection(self):
        for address in (0x3a4644, 0x3a4690, C.SITE, 0x3a0ef4, 0x953568):
            altered = bytearray(self.source)
            altered[address - 0x10000] ^= 1
            with self.assertRaises(ValueError):
                C.guard(altered)

    def test_source_atlas_has_all_five_native_combo_frames(self):
        path = ROOT / 'work/pkg/USRDIR/DATA_REN/TABATA/TPACKPS3.CPK'
        cpk = CPK(str(path)); raw = cpk.read(next(e for e in cpk.files if e['id'] == 2))
        self.assertEqual(R.sha(raw), '93955de0c34e65aa41a44a476c8b05d6b5ffa763200f0f4d70ae8e8bac22e6d4')
        p = 12 + 36 * 6
        self.assertEqual(struct.unpack_from('>HH', raw, p + 20), (80, 400))
        self.assertEqual(raw[p + 12], 0xa5)
        base, length = struct.unpack_from('>II', raw, p + 4)
        self.assertEqual(length, 80 * 400 * 4)
        self.assertLessEqual(base + length, len(raw))
        for frame in range(5):
            pixels = raw[base + frame * 80 * 80 * 4:base + (frame + 1) * 80 * 80 * 4]
            self.assertGreater(max(pixels[::4]), 0)


if __name__ == '__main__':
    unittest.main()
