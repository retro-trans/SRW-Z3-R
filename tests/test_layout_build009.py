"""Both actual Ally/Enemy states, including color and menu geometry."""
from pathlib import Path
import importlib.util
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_game import Build
import rengoku_runtime as R
import rengoku_command_layout as L
import rengoku_map_panel_layout as M
from rengoku_search_layout import FSSA_ASSET, field
from rengoku_roster_settings_layout import x
from rengoku_screenshot_layout import line_width


class Layout009(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT / 'work/pkg').exists():
            raise unittest.SkipTest('Original local assets unavailable')
        cls.build = Build(R.DEFAULT_FONT)
        cls.raw = cls.build.asset(FSSA_ASSET)
        cls.out = cls.build.fssa(cls.raw, cls.build.byasset[FSSA_ASSET])

    def test_selected_side_bright_and_other_side_dim_in_both_states(self):
        expected = (('a0a0ffff', '606060ff'), ('3c3c60ff', 'ffffffff'))
        for state, colors in zip(L.STATES, expected):
            for (row, _, text, selected), color in zip(state, colors):
                self.assertEqual(field(self.out, row), self.build.codec.encode(text))
                self.assertEqual(self.out[row + 12:row + 16].hex(), color)
                self.assertEqual(self.out[row + 15], 255)
                self.assertEqual(self.out[row + 22:row + 32], self.raw[row + 22:row + 32])
                if not selected:
                    # Native multiplication by ANY faction RGB channel
                    # preserves the hue while making the inactive state dark.
                    for old, new in zip(self.raw[row + 12:row + 15], self.out[row + 12:row + 15]):
                        for palette in (64, 128, 192, 255):
                            self.assertLess(new * palette // 255, old * palette // 255 * .4)

    def test_both_states_centered_same_size_with_clear_gap(self):
        for state in L.STATES:
            edges = []
            for row, _, text, _ in state:
                width = line_width(self.build.codec, text, 28)
                edges.append((x(self.out, row) - width / 2, x(self.out, row) + width / 2))
                self.assertEqual(self.out[row + 16:row + 22], bytes((28, 28, 26, 28, 28, 28)))
                self.assertEqual(self.out[row + 8:row + 12], self.raw[0x978ec:0x978f0])
            self.assertAlmostEqual(edges[1][0] - edges[0][1], 10, places=4)
            self.assertAlmostEqual((edges[0][0] + edges[1][1]) / 2, 639.5, places=4)
            self.assertLess(edges[1][1] - edges[0][0], 200)

    def test_only_four_records_change_and_stale_inputs_rejected(self):
        out, report = L.apply_fssa(self.raw, self.raw, self.build.codec)
        rows = [entry[0] for state in L.STATES for entry in state]
        allowed = {p for row in rows for p in range(row, row + 22) if p != row + 15}
        self.assertEqual(len(report), 4)
        self.assertTrue(all(a == b or p in allowed for p, (a, b) in enumerate(zip(self.raw, out))))
        for row in rows:
            bad = bytearray(self.raw)
            bad[row + 22] ^= 1
            with self.assertRaises(ValueError):
                L.apply_fssa(bad, bad, self.build.codec)

    def test_native_renderer_uses_record_tint_and_palette(self):
        # Guard the independently disassembled Rengoku path supporting this
        # data-only fix. No executable instructions are changed by the layer.
        elf = (ROOT / 'work/eboot/EBOOT.ELF').read_bytes()
        self.assertEqual(elf[0x4f770:0x4f774].hex(), '813f000c')  # record RGBA
        self.assertEqual(elf[0x3958:0x3964].hex(), '812280c4906900a44e800020')
        self.assertEqual(elf[0x423c:0x4244].hex(), '807e00a44bfff79d')  # tint -> multiply

    def test_status_strips_keep_every_slot_and_highlight_index(self):
        hooks = M.hooks(self.build.codec)
        for row, jp in M.STRIPS.items():
            encoded = field(self.out, row)
            self.assertEqual(len(encoded), 2 * len(jp))
            self.assertEqual(encoded, hooks[jp.encode('cp932')])
            self.assertEqual(self.out[row + 4:row + 32], self.raw[row + 4:row + 32])
            for i, ch in enumerate(jp):
                # The native indicator selects a two-byte cell by status bit;
                # background and active overlay must select the same label.
                wanted = M.FLAGS.get(ch, ch)
                self.assertEqual(encoded[2 * i:2 * i + 2], self.build.codec.encode(wanted))
                if ch in M.FLAGS:
                    code = self.build.codec.codes[wanted]
                    self.assertEqual(self.build.codec.widths[R.cell(code)], 32)
                    bbox = self.build.codec.glyphs[code].getbbox()
                    self.assertLessEqual(bbox[2] - bbox[0], 28)
                    self.assertGreaterEqual(bbox[0], 2)
        self.assertEqual(len(M.FLAGS), 18)

    def test_popup_labels_fit_and_keep_values_line_spacing_and_states(self):
        for row, (_, en) in M.SUPPORT.items():
            self.assertEqual(field(self.out, row), self.build.codec.encode(en))
            self.assertLessEqual(max(line_width(self.build.codec, s, 18) for s in en.split('\n')), 50)
            self.assertEqual(self.out[row + 4:row + 16], self.raw[row + 4:row + 16])
            self.assertEqual(self.out[row + 21:row + 32], self.raw[row + 21:row + 32])
        for row in M.MOVE:
            self.assertEqual(field(self.out, row), self.build.codec.encode('MV'))
            self.assertLessEqual(line_width(self.build.codec, 'MV', 22), 36)
            self.assertEqual(self.out[row + 21:row + 32], self.raw[row + 21:row + 32])
        for row in M.FOCUS:
            self.assertEqual(field(self.out, row), self.build.codec.encode('Foc'))
            self.assertEqual(self.out[row + 4:row + 32], self.raw[row + 4:row + 32])
        self.assertEqual(field(self.out, M.RECOVERY), self.build.codec.encode('Rec:\nRec:'))
        self.assertEqual(self.out[M.RECOVERY + 4:M.RECOVERY + 32], self.raw[M.RECOVERY + 4:M.RECOVERY + 32])

    def test_confirmation_records_keep_native_columns(self):
        # Actual drawing with unequal quad/pitch is exercised by build012's
        # emitted-PPC tests. A generic proportional width sum is invalid for
        # the runtime tab and previously missed the nine-pixel regression.
        pad = self.build.codec.codes[R.CHOICE_PAD]
        self.assertIsNone(self.build.codec.glyphs[pad].getbbox())
        self.assertEqual(self.build.codec.widths[R.cell(pad)], 32)
        for bg, active, text in M.CHOICES:
            self.assertEqual(field(self.out, bg), self.build.codec.encode(M.CHOICE_TEXT))
            self.assertEqual(self.out[bg + 4:bg + 32], self.raw[bg + 4:bg + 32])
            self.assertEqual(self.out[active + 23] & 0x40, 0)
            self.assertEqual(self.out[active + 8:active + 23], self.raw[active + 8:active + 23])
            column = 0 if text == 'Yes' else 125
            self.assertAlmostEqual(x(self.out, active) - x(self.out, bg), column, places=4)

    def test_new_map_layer_changes_only_scoped_records(self):
        # Simulate preceding translation layers without rerunning them; restore
        # just this layer's metadata, then apply and compare every byte.
        before = bytearray(self.out)
        rows = set(M.STRIPS) | set(M.SUPPORT) | set(M.MOVE) | set(M.FOCUS) | {M.RECOVERY}
        rows.update(r for pair in M.CHOICES for r in pair[:2])
        for row in rows:
            before[row + 4:row + 32] = self.raw[row + 4:row + 32]
        after, _ = M.apply_fssa(self.raw, before, self.build.codec)
        allowed = {p for row in rows for p in range(row, row + 4)}
        allowed.update(p for row in set(M.SUPPORT) | set(M.MOVE) for p in range(row + 16, row + 21))
        for _, row, _ in M.CHOICES:
            allowed.update(range(row + 4, row + 8)); allowed.add(row + 23)
        self.assertTrue(all(a == b or p in allowed for p, (a, b) in enumerate(zip(before, after))))

    def test_all_spirit_masks_match_z31_reference_rasterizer(self):
        from PIL import Image
        path = ROOT.parent / 'SRW Z3/tools/ttfglyph.py'
        if not path.exists():
            self.skipTest('Read-only font reference unavailable')
        spec = importlib.util.spec_from_file_location('reference_face009', str(path))
        ref = importlib.util.module_from_spec(spec)
        old = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(path.parent))
        try:
            spec.loader.exec_module(ref)
        finally:
            sys.path.pop(0)
            sys.dont_write_bytecode = old
        face = ref.Face(str(R.DEFAULT_FONT), 16, 23, 0, 0.3)
        for pua, word in R.SPIRIT_LABELS.items():
            parts = []
            for im, _, top, _ in [face.natural(c) for c in word]:
                box = im.getbbox()
                parts.append((im.crop(box), 23 + top + box[1]))
            natural = sum(im.width for im, _ in parts)
            budget = min(natural, 28 - 2 * (len(parts) - 1))
            cov = bytearray(1024)
            x = (32 - budget - 2 * (len(parts) - 1)) // 2
            total = previous = 0
            for im, y in parts:
                total += im.width
                edge = round(total * budget / natural)
                width = edge - previous
                previous = edge
                face._blit(cov, im.resize((width, im.height), Image.Resampling.BOX), x, y)
                x += width + 2
            self.assertEqual(self.build.codec.glyphs[self.build.codec.codes[pua]].tobytes(), bytes(cov), word)


if __name__ == '__main__':
    unittest.main()
