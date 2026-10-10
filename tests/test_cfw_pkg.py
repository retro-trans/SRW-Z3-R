"""Focused container checks; no original game data required."""
import hashlib
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from package_cfw_pkg import STAGE, authenticated_prefix, debug_crypt, layout, make_header


class CfwPackageTests(unittest.TestCase):
    def test_debug_stream_counter_and_unaligned_range(self):
        seed = bytes(range(16))
        plain = bytes(range(99))
        encrypted = debug_crypt(seed, plain)
        self.assertEqual(debug_crypt(seed, encrypted), plain)
        self.assertEqual(debug_crypt(seed, encrypted[13:86], 13), plain[13:86])
        prefix = seed[:8]*2 + seed[8:]*2 + bytes(24)
        self.assertEqual(encrypted[:16], bytes(a ^ b for a, b in zip(
            plain[:16], hashlib.sha1(prefix + bytes(8)).digest())))
        with self.assertRaises(ValueError):
            debug_crypt(b'short', plain)

    def test_stage_raw_and_self_unmodified_sized(self):
        entries = [dict(path='USRDIR', flags=0x80000004, directory=True),
                   dict(path='USRDIR/EBOOT.BIN', flags=0x80000001, directory=False),
                   dict(path=STAGE, flags=0x80000009, directory=False)]
        rows, table, size = layout(entries, {'USRDIR/EBOOT.BIN': {'bytes': 113}, STAGE: {'bytes': 39}})
        self.assertEqual(rows[1]['size'], 113)
        self.assertEqual(rows[1]['flags'], 0x80000001)
        self.assertEqual(rows[2]['flags'], 0x80000003)
        self.assertEqual(rows[2]['offset'] % 16, 0)
        self.assertEqual(size, rows[2]['offset'] + 48)
        self.assertEqual(len(table), rows[0]['offset'])
        with self.assertRaises(ValueError):
            layout([dict(path='../evil', directory=True)], {})

    def test_debug_authentication_prefix(self):
        meta = struct.pack('>III', 1, 4, 2) + struct.pack('>IIQ', 4, 8, 256) + bytes(4)
        header = make_header(3, 256, len(meta), 2, bytes(range(16)))
        self.assertEqual(struct.unpack_from('>HH', header, 4), (0, 1))
        self.assertEqual(struct.unpack_from('>I', header, 0x14)[0], 3)
        prefix = authenticated_prefix(header, meta)
        self.assertEqual(len(prefix), struct.unpack_from('>Q', header, 0x20)[0])
        hs = hashlib.sha1(header).digest()[3:19]
        ms = hashlib.sha1(meta).digest()[3:19]
        self.assertEqual(prefix[128:144], hs)
        self.assertEqual(debug_crypt(ms, debug_crypt(hs, prefix[144:192])), bytes(48))
        self.assertEqual(prefix[192+len(meta):208+len(meta)], ms)


if __name__ == '__main__':
    unittest.main()
