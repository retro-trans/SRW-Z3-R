"""Source-bound regression checks for the five build018 screenshot reports."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_game import Build
from rengoku_runtime import DEFAULT_FONT
from rengoku_screenshot_layout import line_width
import rengoku_report_layout as G
from rengoku_category_layout import wrap
import localization
from test_screenshot_runtime import Machine


class Category021(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT/'work/pkg').exists():
            raise unittest.SkipTest('Local source unavailable')
        cls.b = Build(DEFAULT_FONT)

    def assert_lookup(self,h,key,value):
        for method in ('draw','converted'):
            machine = Machine(self.b.codec,h)
            if method == 'converted':
                machine.put(machine.state+0xb8,key+b'\0')
            machine.run(method,key)
            self.assertEqual(machine.cstr(machine.r[31 if method=='converted' else 3]),value)

    def test_episode10_complete_condition_and_native_table(self):
        asset = 'work/story/STGZ3REN_00061.lua'
        raw = (ROOT/asset).read_bytes()
        built = self.b.lua(raw,asset,'STGZ3REN_00061')
        pattern = rb'OPERATE_TBL\s*=\s*\{\s*str_tbl\s*=\s*\{(.*?)\}\s*;'
        self.assertEqual(re.search(pattern,raw,re.S)[1],re.search(pattern,built,re.S)[1])
        jp = '敵ユニットを１機も町に侵入させず、全滅させる。'.encode('cp932')
        english = self.b.operation_hooks[jp]
        self.assertEqual(english,self.b.codec.encode(wrap(self.b.codec,
            'Defeat all enemies without letting a single enemy unit enter the town.',950)))
        self.assert_lookup(self.b.operation_hooks,jp,english)

    def test_all_gift_tables_retain_their_original_tuple(self):
        census = []
        for path in sorted((ROOT/'work/story').glob('*.lua')):
            raw = path.read_bytes()
            source = raw.decode('latin1')
            if not G.spans(source):
                continue
            asset = path.relative_to(ROOT).as_posix()
            built = self.b.lua(raw,asset,path.stem).decode('latin1')
            self.assertEqual([source[a:z] for a,z in G.spans(source)],
                             [built[a:z] for a,z in G.spans(built)])
            census.extend((asset,a) for a,z in G.spans(source))
        self.assertEqual(len(census),1)
        self.assertEqual(census[0][0],'work/story/STGZ3REN_00073.lua')
        row = self.b.occ['nd:ee9bde9a9e48e8eb1a79']
        h,proof = G.hooks(row,self.b.codec)
        self.assertEqual(proof['display'].split(),row['english'].split())
        self.assertEqual(proof['native_lines'],2)
        self.assertLessEqual(max(proof['line_widths']),1050)
        for key,value in h.items():
            self.assertEqual(self.b.report_hooks[key],value)
            self.assert_lookup(h,key,value)

    def test_names_across_the_canonical_corpus(self):
        count = 0
        for path in sorted((ROOT/'localization/locales/en').glob('*.json')):
            data = json.loads(path.read_text(encoding='utf8'))
            for identity,row in data.get('messages',{}).items():
                text = row.get('text') or ''
                self.assertNotIn('Dowen',text,(path.name,identity))
                if 'デイモーン' in (row.get('source') or ''):
                    self.assertNotRegex(text,r'\bDemon\b')
                count += 1
        self.assertGreater(count,6000)
        terms = localization.terms()
        self.assertEqual({t['en'] for t in terms if t['jp']=='アサキム・ドーウィン'},
                         {'Asakim Dowin'})
        self.assertEqual({t['en'] for t in terms if t['jp']=='デイモーン'}, {'Daimon'})
        text = self.b.locale['messages']['library:8581931f0b5ea6b9']['text']
        self.assertIn("demon king's sword",text)


if __name__ == '__main__':
    unittest.main()
