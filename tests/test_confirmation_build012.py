"""Reproduce the nine-pixel regression using Rengoku's real font preset.

Execute native glyph-style selection and the patched pen-advance loop.
This is instruction-level validation, not an RPCS3 gameplay capture.
"""
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_game import Build
from cpk import CPK
import rengoku_runtime as R
import rengoku_map_panel_layout as M
from rengoku_search_layout import FSSA_ASSET, field
from test_link_runtime import CPU

# Exact advance adapter shipped in 009--011, before live-pitch tabs.
OLD_ADVANCE = bytes.fromhex(
    'a00100c23d20008f6129e0007c0900ae2c0000204082000cc1a100944800002c'
    'f80100d0c9a100d0fda06e9cfda06818c141009cedad02b23d203d00912100d0'
    'c14100d0edad02b23d2000ce61299000c1490000ed4a682ad14900004e800020')


def f32(v):
    return struct.unpack('>f', struct.pack('>f', v))[0]


class Confirmation012(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT / 'work/pkg').exists() or not R.DEFAULT_FONT.exists():
            raise unittest.SkipTest('Original local assets unavailable')
        cls.build = Build(R.DEFAULT_FONT)
        cls.raw = cls.build.asset(FSSA_ASSET)
        cls.out = cls.build.fssa(cls.raw, cls.build.byasset[FSSA_ASSET])
        cls.elf, cls.report = R.patch_elf(cls.build.original_elf, cls.build.codec, {})
        cls.codec = cls.build.codec
        cpk = CPK(str(ROOT / 'work/pkg/USRDIR/DATA_REN/AIDDATA/AIDDATAPACK_R.CPK'))
        cls.styles = cpk.read(next(e for e in cpk.files if e['id'] == 4))

    def cpu(self, legacy=False):
        c = CPU(self.elf)
        if legacy:
            c.put(self.report['stubs']['advance'], OLD_ADVANCE)
            pad = R.cell(self.codec.codes[R.CHOICE_PAD])
            c.put(R.WIDTHS + pad, bytes([41]))
        return c

    def draw(self, c, text, origin, quad=28, pitch=25):
        # Preset 1, left-aligned FSSA style, as set by 0x5f65c/0x13abc.
        state = 0x2200000
        c.put(state, bytes(0xc0))
        for off, value in ((0x54, quad), (0x58, quad), (0x5c, pitch),
                           (0x60, pitch), (0x78, quad), (0x7c, quad),
                           (0x80, pitch), (0x84, pitch), (0x88, quad - 2),
                           (0x8c, quad), (0x90, pitch - 2), (0x94, pitch)):
            c.put(state + off, struct.pack('>f', value))
        c.put(state + 0xac, b'\0\1')
        c.put(R.SCRATCH, bytes(4))
        c.f[31] = f32(origin)
        c.put(c.r[1] + 0x84, struct.pack('>f', origin))
        result = []
        for pos in range(0, len(text), 2):
            glyph = text[pos:pos + 2]
            c.r[30] = state
            c.r[31] = 0x2210001
            c.r[9] = glyph[0]
            c.r[10] = 0  # native DRAW's ordinary-glyph mode, from sp+0xa8
            c.put(0x2210001, glyph[1:])
            c.put(c.r[1] + 0xb0, bytes(4))
            # Run the game's real code selecting quad/pitch for this glyph.
            c.run(0x144c8, {0x145e0})
            x = struct.unpack('>f', c.read(c.r[1] + 0x84, 4))[0]
            size = struct.unpack('>2f', c.read(c.r[1] + 0x9c, 8))
            result.append((glyph, x, size))
            cell = R.cell(int.from_bytes(glyph, 'big'))
            c.put(c.r[1] + 0xc2, struct.pack('>H', cell))
            # Includes the native add/store after the emitted advance stub.
            c.run(0x147d8, {0x147e8})
        pen = struct.unpack('>f', c.read(c.r[1] + 0x84, 4))[0]
        acc = struct.unpack('>f', c.read(R.SCRATCH, 4))[0]
        self.assertAlmostEqual(acc, pen - f32(origin), places=3)
        return result

    def test_real_preset_separates_quad_and_pitch(self):
        self.assertEqual(struct.unpack_from('>I', self.styles, 0x484)[0], 13)
        self.assertEqual(struct.unpack_from('>8h', self.styles, 0x498),
                         (28, 28, 26, 28, 28, 28, 26, 28))
        source = self.build.original_elf
        # Native loader places member 4's table at the renderer's +0x518.
        for va, expected in (
            (0x5e188, '91630488'),
            (0x61410, '3876009880960548786300204bffcc3d'),
            (0x5f63c, '7880c7222f890000540020367fa05a14'),
            (0x5f660, '891f001088ff001188df001288bf0013a01d0000a13d0002')):
            self.assertEqual(source[va - 0x10000:va - 0x10000 + len(expected)//2].hex(), expected)
        for bg, active, _ in M.CHOICES:
            for row in (bg, active):
                self.assertEqual(self.out[row + 22] & 15, 1)
                self.assertEqual(self.out[row + 23] & 0x7f, 0)
                self.assertEqual(self.out[row + 16], 25)

    def test_previous_build_reproduces_nine_pixel_no_error(self):
        row = self.draw(self.cpu(legacy=True), self.codec.encode(M.CHOICE_TEXT), 552)
        self.assertEqual(row[-2][1], 552 + 134)
        self.assertEqual(row[-2][1] - (552 + 125), 9)

    def test_all_six_overlays_match_background_glyph_positions(self):
        for bg, active, word in M.CHOICES:
            bgx = f32(struct.unpack_from('>f', self.out, bg + 4)[0] * 640 + 640)
            ax = f32(struct.unpack_from('>f', self.out, active + 4)[0] * 640 + 640)
            background = self.draw(self.cpu(), field(self.out, bg), bgx)
            selected = self.draw(self.cpu(), field(self.out, active), ax)
            expected = background[:3] if word == 'Yes' else background[-2:]
            for actual, wanted in zip(selected, expected):
                self.assertEqual(actual, wanted, hex(active))

    def test_tab_uses_live_pitch_across_scales_and_preserves_abi(self):
        for origin in (0, -88.5, 552, 703.25):
            for pitch in (25, 31, 37.28):
                for quad in (23.3, 25, 28, 40):
                    row = self.draw(self.cpu(), self.codec.encode(M.CHOICE_TEXT), origin, quad, pitch)
                    self.assertAlmostEqual(row[4][1], origin + 3 * pitch, places=3)
                    self.assertAlmostEqual(row[-2][1], origin + 5 * pitch, places=3)
        # The new branch has exactly the same clobbers as ordinary advance.
        for ch in ('Y', R.CHOICE_PAD, '／', '日'):
            c = self.cpu()
            cell = R.cell(int.from_bytes(self.codec.encode(ch), 'big'))
            c.put(c.r[1] + 0xc2, struct.pack('>H', cell))
            for off, value in ((0x84, 580.5), (0x94, 25), (0x9c, 28)):
                c.put(c.r[1] + off, struct.pack('>f', value))
            c.put(R.SCRATCH, struct.pack('>f', 28.5));c.f[31] = 552
            regs, floats, cr = c.r[:], c.f[:], c.cr[:]
            c.run(self.report['stubs']['advance'], {c.lr})
            self.assertTrue(all(c.r[i] == regs[i] for i in set(range(32)) - {0, 9}))
            self.assertTrue(all(c.f[i] == floats[i] for i in set(range(32)) - {10, 13}))
            self.assertEqual(c.cr[1:], cr[1:])
            self.assertTrue(c.writes <= (set(range(c.r[1] - 0x4000, c.r[1] + 0x4400)) |
                                        set(range(R.SCRATCH, R.SCRATCH + 4))))
        for ch in list(self.codec.codes) + ['／', '　', '日']:
            if ch == R.CHOICE_PAD:
                continue
            glyph = int.from_bytes(self.codec.encode(ch), 'big')
            cell = R.cell(glyph)
            for quad, pitch in ((28, 25), (23.3, 31)):
                c = self.cpu()
                c.put(c.r[1] + 0xc2, struct.pack('>H', cell))
                c.put(c.r[1] + 0x94, struct.pack('>f', pitch))
                c.put(c.r[1] + 0x9c, struct.pack('>f', quad))
                c.put(R.SCRATCH, bytes(4))
                c.run(self.report['stubs']['advance'], {c.lr})
                width = self.codec.widths.get(cell, 32)
                expected = pitch if width == 32 else f32(width * f32(quad)) / 32
                self.assertEqual(c.f[13], expected, repr(ch))


if __name__ == '__main__':
    unittest.main()
