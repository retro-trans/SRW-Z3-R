"""Real SRVC cue readback, native escape conversion and subtitle boundaries."""
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_game import Build
import battle_lines
import rengoku_runtime as R
import rengoku_battle_subtitles as L
from rengoku_screenshot_layout import line_width
from test_link_runtime import CPU


class BattleSubtitles014(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT / 'work/pkg').exists():
            raise unittest.SkipTest('Original local assets unavailable')
        cls.build = Build(R.DEFAULT_FONT)
        cls.codec = cls.build.codec
        cls.changes = {r['message']: r for r in cls.build.subtitle_report['changed']}

    def test_reported_blue_line_fits_without_shrinking_or_rewording(self):
        row = self.changes['battle:bb4a3ab0560dceda']
        self.assertEqual(row['after'],
                         "「Mass-produced or not,\\nI can't let this get scratched!」")
        self.assertGreater(line_width(self.codec, row['before'], 31), L.WIDTH)
        for line in row['after'].split(L.BREAK):
            # Native screenshot: origin about 276, status block about 1027.
            self.assertLessEqual(276 + line_width(self.codec, line, 32), 1006)
        self.assertEqual(row['before'].split(), row['after'].replace(L.BREAK, ' ').split())

    def test_native_rengoku_converter_emits_lf_and_preserves_adjacent_state(self):
        c = CPU(self.build.original_elf)
        c.r[2] = 0x953f88
        source, dest = 0x2200000, 0x2210000
        row = self.changes['battle:bb4a3ab0560dceda']
        encoded = self.codec.encode(row['after'])
        c.put(source, encoded + b'\0')
        c.put(dest, b'\xcc' * (L.BUFFER_BYTES + 8))
        c.r[3], c.r[4] = dest, source
        c.calls[0x67db24] = lambda cpu: (
            cpu.r[3] + cpu.string(cpu.r[3]).find(cpu.string(cpu.r[4]))
            if cpu.string(cpu.r[4]) in cpu.string(cpu.r[3]) else 0)
        def copy_n(cpu):
            cpu.put(cpu.r[3], cpu.read(cpu.r[4], cpu.r[5]))
            return cpu.r[3]
        def copy_z(cpu):
            cpu.put(cpu.r[3], cpu.string(cpu.r[4]) + b'\0')
            return cpu.r[3]
        c.calls[0x6832c0], c.calls[0x682eac] = copy_n, copy_z
        c.run(0x12c3b4, {0x10000})
        expected = encoded.replace(b'\\n', b'\n')
        self.assertEqual(c.string(dest), expected)
        self.assertEqual(c.read(dest + L.BUFFER_BYTES, 8), b'\xcc' * 8)
        self.assertEqual(c.r[1], 0x2000000)

    def test_every_changed_entry_keeps_words_and_native_capacity(self):
        self.assertGreater(len(self.changes), 400)
        for row in self.changes.values():
            before, after = row['before'], row['after']
            self.assertEqual(before.replace(L.BREAK, ' ').split(), after.replace(L.BREAK, ' ').split())
            self.assertEqual(after.count(L.BREAK), 1)
            self.assertLessEqual(len(L.native_bytes(self.codec, after)), L.BUFFER_BYTES)
            self.assertTrue(all(line_width(self.codec, s, 32) <= L.WIDTH
                                for s in after.split(L.BREAK)))
        for row in self.build.subtitle_report['pending']:
            self.assertEqual(L.fit(self.codec, row['before'])[0], row['before'])
        for text in ('「Short.」', '「Already\\nsplit.」'):
            self.assertEqual(L.fit(self.codec, text), (text, None))
        for text in ('「$n attacks!」', '「%s attacks!」', '「Bad\\rcontrol」'):
            with self.assertRaises(ValueError):
                L.fit(self.codec, text)

    def test_all_6356_cues_keep_metadata_and_resolve_expected_display_text(self):
        b = self.build
        raw = (ROOT / 'work/pkg/USRDIR/DATA_REN/BTLC/SRVC.BIN').read_bytes()
        _, _, original = battle_lines.discover_table(raw, b.original_elf)
        new_table = struct.unpack('>40I', b.srvc_edit[2])
        # Re-read binary headers, without asking Python's CP932 decoder to
        # interpret the deliberately assigned empty atlas cells as Japanese.
        generated = []
        for base in new_table[:-1]:
            n1, n2, n3 = b.srvc[base + 1:base + 4]
            n4, cues = struct.unpack_from('<HH', b.srvc, base + 4)
            index = base + 8 + n1*4 + n4*8 + n2*8 + n3*4 + cues*8
            generated.append({'base': base, 'index': index, 'pool': index + cues*4})
        by_offset = {r['offset']: r for r in b.bocc.values() if isinstance(r.get('bank'), int)}
        count = 0
        for old, new in zip(original, generated):
            self.assertEqual(raw[old['base']:old['index']], b.srvc[new['base']:new['index']])
            for i in range(old['count']):
                source = old['pool'] + struct.unpack_from('<I', raw, old['index'] + 4*i)[0]
                target = new['pool'] + struct.unpack_from('<I', b.srvc, new['index'] + 4*i)[0]
                row = by_offset.get(source)
                want = (self.codec.encode(L.fit(self.codec, row['english'])[0]) if row
                        else raw[source:raw.index(b'\0', source)])
                self.assertEqual(b.srvc[target:b.srvc.index(b'\0', target)], want)
                if old['bank'] == 19 and i == 103:
                    self.assertIn(b'\\n', want)
                count += 1
        self.assertEqual(count, 6356)


if __name__ == '__main__':
    unittest.main()
