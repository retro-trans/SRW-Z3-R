"""CFW candidate audit rejection checks; fixtures remain read-only."""
import json
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from package_cfw_overlay import ROOT, audit_program
from rengoku_runtime import CODE, branch


class CfwAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build = ROOT / 'work/builds/rengoku_en_018'
        if not (build / 'BUILD_REPORT.json').exists():
            raise unittest.SkipTest('Private verified build fixture unavailable')
        cls.original = (ROOT / 'work/eboot/EBOOT.ELF').read_bytes()
        cls.original_self = (ROOT / 'work/pkg/USRDIR/EBOOT.BIN').read_bytes()
        cls.elf = (build / 'intermediate/EBOOT.ELF').read_bytes()
        cls.wrapped = (build / 'PS3/NPJB00689/USRDIR/EBOOT.BIN').read_bytes()
        cls.runtime = json.loads((build / 'BUILD_REPORT.json').read_text(encoding='utf8'))['runtime']

    def check(self, elf=None, wrapped=None):
        return audit_program(self.original, elf or self.elf,
                             wrapped or self.wrapped, self.original_self, self.runtime)

    def test_actual_candidate_has_only_native_rx_rw_loads(self):
        proof = self.check()
        self.assertEqual(proof['active_native_loads'], 2)
        self.assertGreater(proof['direct_hook_branches_checked'], 0)

    def test_writable_code_or_changed_tls_is_rejected(self):
        modified = bytearray(self.elf)
        struct.pack_into('>I', modified, 64 + 4, 7)
        with self.assertRaises(ValueError):
            self.check(bytes(modified))
        modified = bytearray(self.elf)
        modified[64 + 5 * 56 + 24] ^= 1
        with self.assertRaisesRegex(ValueError, 'TLS/process'):
            self.check(bytes(modified))

    def test_unrecorded_original_instruction_change_is_rejected(self):
        modified = bytearray(self.elf)
        modified[0x1000] ^= 1
        with self.assertRaisesRegex(ValueError, 'Unrecorded original program'):
            self.check(bytes(modified))

    def test_hook_branch_into_non_executable_memory_is_rejected(self):
        modified = bytearray(self.elf)
        struct.pack_into('>I', modified, CODE - 0x10000, branch(CODE, 0x1000000))
        with self.assertRaisesRegex(ValueError, 'branch outside executable'):
            self.check(bytes(modified))

    def test_self_payload_and_application_identity_cannot_differ(self):
        modified = bytearray(self.wrapped)
        modified[-1] ^= 1
        with self.assertRaisesRegex(ValueError, 'SELF payload differs'):
            self.check(wrapped=bytes(modified))
        modified = bytearray(self.wrapped)
        app = struct.unpack_from('>Q', modified, 0x28)[0]
        modified[app] ^= 1
        with self.assertRaisesRegex(ValueError, 'NPDRM application'):
            self.check(wrapped=bytes(modified))


if __name__ == '__main__':
    unittest.main()
