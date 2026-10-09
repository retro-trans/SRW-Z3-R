"""Regression checks for archive boundaries and source/translation binding."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import localization as L
from pkg_extract import safe_relative
from verify_source import long_strings


class ContentChecks(unittest.TestCase):
    def setUp(self):
        self.glossary = [{'id': 'pilot:blue', 'jp': 'ブルー', 'en': 'Blue', 'status': 'researched'},
                         {'id': 'a', 'jp': '甲', 'en': 'Alpha', 'status': 'researched'},
                         {'id': 'b', 'jp': '乙', 'en': 'Beta', 'status': 'researched'}]
        self.row = {'jp': 'ブルー\n「《甲》と《乙》、$n」', 'pid': 'pid_BLUE', 'sha': '123', 'source_member_sha256': 'abc'}
        self.entry = {'text': '$$ブルー$$\n「《$$甲$$》 and 《$$乙$$》, $n」', 'status': 'draft', 'source_sha': '123', 'source_member_sha256': 'abc'}

    def test_valid_glossary_links_and_placeholder(self):
        self.assertEqual(L.validate(self.row, self.entry, self.glossary), ([], []))

    def test_reordered_links_fail_even_with_equal_counts(self):
        self.entry['text'] = '$$ブルー$$\n「《$$乙$$》 and 《$$甲$$》, $n」'
        errors, _ = L.validate(self.row, self.entry, self.glossary)
        self.assertTrue(any('label/order' in e for e in errors))

    def test_dropped_placeholder_fails(self):
        self.entry['text'] = self.entry['text'].replace('$n', 'you')
        self.assertIn('Runtime placeholders changed', L.validate(self.row, self.entry, self.glossary)[0])

    def test_stale_source_member_fails(self):
        self.entry['source_member_sha256'] = 'old'
        self.assertIn('Source member fingerprint mismatch', L.validate(self.row, self.entry, self.glossary)[0])

    def test_wrong_speaker_fails(self):
        self.entry['text'] = self.entry['text'].replace('$$ブルー$$', 'Advent')
        self.assertIn('Speaker disagrees with glossary', L.validate(self.row, self.entry, self.glossary)[0])

    def test_ambiguous_name_requires_discriminator(self):
        self.glossary.append({'id': 'other_blue', 'jp': 'ブルー', 'en': 'Blu', 'status': 'researched'})
        with self.assertRaises(ValueError):
            L.expand('$$ブルー$$', self.glossary)
        self.assertEqual(L.expand('$$ブルー#pilot:blue$$', self.glossary), 'Blue')

    def test_japanese_readings_are_not_monologue_wrappers(self):
        self.row['jp'] = 'ブルー\n「蒼（あお）の地球」'
        self.entry['text'] = '$$ブルー$$\n「Blue Earth」'
        self.assertEqual(L.validate(self.row, self.entry, self.glossary), ([], []))

    def test_unknown_link_needs_explicit_label(self):
        self.row['jp'] = 'ブルー\n「《彼等》」'
        self.entry['text'] = '$$ブルー$$\n「《them》」'
        self.assertTrue(L.validate(self.row, self.entry, self.glossary)[0])
        self.entry['link_labels'] = {'彼等': 'them'}
        self.assertEqual(L.validate(self.row, self.entry, self.glossary), ([], []))


class ArchiveChecks(unittest.TestCase):
    def test_windows_archive_traversal_and_devices_rejected(self):
        for name in ('../x', '/x', 'C:/x', 'USRDIR/../../x', 'a\\b', 'a//b', 'a/./b', 'NUL.txt', 'a/x. '):
            with self.subTest(name=name), self.assertRaises(ValueError):
                safe_relative(name)
        self.assertEqual(str(safe_relative('USRDIR/DATA_REN/STAGE/A.SDAT')), 'USRDIR/DATA_REN/STAGE/A.SDAT')

    def test_lexer_ignores_comments_and_quoted_fake_records(self):
        text = '-- [[fake]]\n--[=[[[fake2]]]=]\nx="[[fake3]]"; y=[[real]]; z=[=[second]=]'
        self.assertEqual(long_strings(text), ['real', 'second'])


if __name__ == '__main__':
    unittest.main()
