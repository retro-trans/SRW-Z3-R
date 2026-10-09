"""Installer rejects unsafe paths and mismatched inputs before creating files."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from apply_release import apply, identity, inside


class InstallerChecks(unittest.TestCase):
    def test_path_escape_and_windows_paths_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for value in ('../EBOOT.BIN', '/absolute', 'C:/outside', 'USRDIR/../../outside', 'USRDIR\\outside'):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    inside(root, value)

    def test_corrupt_source_and_patch_create_no_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); bundle = root / 'bundle'; source = root / 'source'
            bundle.mkdir(); source.mkdir()
            (source / 'PARAM.SFO').write_bytes(b'correct original')
            patch = bundle / 'file.xdelta'; patch.write_bytes(b'correct patch')
            manifest = {'schema': 'srw-z3-r-file-patches-v1', 'title_id': 'NPJB00689',
                        'source_files': {'PARAM.SFO': identity(source / 'PARAM.SFO')},
                        'patches': [{'patch': 'file.xdelta', 'patch_identity': identity(patch)}]}
            (bundle / 'BUILD-MANIFEST.json').write_text(json.dumps(manifest), encoding='utf8')
            (source / 'PARAM.SFO').write_bytes(b'wrong source')
            with self.assertRaisesRegex(ValueError, 'Original input mismatch'):
                apply(bundle, source, root / 'output', 'missing-xdelta', True)
            self.assertFalse((root / 'output').exists())
            (source / 'PARAM.SFO').write_bytes(b'correct original')
            patch.write_bytes(b'wrong patch')
            with self.assertRaisesRegex(ValueError, 'Patch download mismatch'):
                apply(bundle, source, root / 'output', 'missing-xdelta', True)
            self.assertFalse((root / 'output').exists())

    def test_existing_or_nested_output_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); bundle = root / 'bundle'; source = root / 'source'
            bundle.mkdir(); source.mkdir()
            (bundle / 'BUILD-MANIFEST.json').write_text(json.dumps(
                {'schema': 'srw-z3-r-file-patches-v1', 'title_id': 'NPJB00689'}), encoding='utf8')
            for output in (source, source / 'nested', root):
                with self.assertRaisesRegex(ValueError, 'new output folder'):
                    apply(bundle, source, output, 'missing-xdelta', True)


if __name__ == '__main__':
    unittest.main()
