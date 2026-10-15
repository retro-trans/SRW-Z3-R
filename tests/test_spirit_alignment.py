"""Spirit command identities, composite references and native status slots."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import align_spirit_terms as alignment
import rengoku_map_panel_layout as panel
import rengoku_runtime as runtime


class SpiritAlignment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.names, _ = alignment.reference('spirits')
        cls.rows = json.loads((ROOT / 'localization/locales/en/non_dialogue.json')
                             .read_text(encoding='utf8'))['messages']

    def test_all_shared_command_names_match_japanese_identities(self):
        names = {r['source']: r['text'] for r in self.rows.values()
                 if r['source'] in self.names}
        self.assertEqual(len(names), 42)
        self.assertEqual(len(set(names.values())), 42)
        for jp, text in names.items():
            self.assertEqual(text, self.names[jp], jp)
        self.assertEqual(names['直撃'], 'Break')
        self.assertEqual(names['闘志'], 'Fury')

    def test_related_effects_and_unrelated_skill_are_distinct(self):
        bravery = self.rows['gameplay:25dd712b0d0ac76e']['text']
        self.assertIn('Break', bravery)
        self.assertNotIn('Fury', bravery)
        deployment = self.rows['interface:381a9435a3dad092']['text']
        self.assertIn('Fury', deployment)
        self.assertNotIn('Fighting Spirit', deployment)
        skills = [r['text'] for r in self.rows.values() if r['source'] == '戦意高揚']
        self.assertTrue(skills)
        self.assertTrue(all(s == 'Fighting Sp' for s in skills))
        ordinary = 'A treasure holding the fighting spirit of its warriors.'
        self.assertEqual(alignment.target('戦士達の闘志', ordinary, self.names), ordinary)

    def test_normalization_is_idempotent_and_current_sources_are_clean(self):
        for jp in ('熱魂闘閃不鉄集必加覚手狙突直幸努乱',
                   '熱魂闘閃不鉄集必加覚手狙突直／乱分'):
            old = next(r['previous'] for r in alignment.read(alignment.AUDIT)['changes']
                       if r['source'] == jp)
            once = alignment.target(jp, old, self.names)
            self.assertIn('Fury', once)
            self.assertIn('Break', once)
            self.assertEqual(alignment.target(jp, once, self.names), once)
        outputs, audit = alignment.plan()
        self.assertFalse(outputs)
        self.assertFalse(audit['changes'])

    def test_native_strip_slots_keep_japanese_identity_and_order(self):
        self.assertEqual(runtime.SPIRIT_LABELS[panel.FLAGS['闘']], 'Fu')
        self.assertEqual(runtime.SPIRIT_LABELS[panel.FLAGS['直']], 'Br')
        for jp in panel.STRIPS.values():
            shown = panel.status_text(jp)
            self.assertEqual(len(shown), len(jp))
            self.assertEqual(shown.index(panel.FLAGS['闘']), jp.index('闘'))
            self.assertEqual(shown.index(panel.FLAGS['直']), jp.index('直'))
            self.assertEqual(shown.count('／'), jp.count('／'))


if __name__ == '__main__':
    unittest.main()
