"""Focused safety/layout checks for the RPCS3-only package wrapper."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from repack_runtime_pkg import cipher, placement


class RuntimePackageTests(unittest.TestCase):
    def test_shrink_preserves_offsets_growth_appends_aligned(self):
        entries = [dict(path='small', size=100, offset=64, directory=False),
                   dict(path='unchanged', size=200, offset=176, directory=False),
                   dict(path='large', size=16, offset=384, directory=False)]
        plan, size = placement(entries, ['small', 'large'],
                               {'small': 48, 'large': 33}, 400)
        self.assertEqual([(r['path'], r['offset'], r['size'], r['appended'])
                          for r in plan], [('small', 64, 48, False),
                                          ('large', 400, 33, True)])
        self.assertEqual(size, 448)

    def test_missing_directory_or_unaligned_replacements_fail(self):
        with self.assertRaises(ValueError):
            placement([], ['missing'], {}, 0)
        for entry in (dict(path='x', size=0, offset=0, directory=True),
                      dict(path='x', size=20, offset=3, directory=False)):
            with self.assertRaises(ValueError):
                placement([entry], ['x'], {'x': 16}, 32)

    def test_stream_offset_agrees_with_contiguous_encryption(self):
        plain = bytes(range(256)) * 4
        whole = cipher(1234, 0).update(plain)
        segment = cipher(1234, 48).update(plain[48:])
        self.assertEqual(whole[48:], segment)
        self.assertEqual(cipher(1234, 48).update(segment), plain[48:])
        with self.assertRaises(ValueError):
            cipher(1234, 1)


if __name__ == '__main__':
    unittest.main()
