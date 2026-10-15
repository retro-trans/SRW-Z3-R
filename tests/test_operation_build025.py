"""Exercise the exact numbered/continuation strings seen by the native drawer."""
from pathlib import Path
import re
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_game import Build,DEFAULT_FONT
import rengoku_operation_layout as O
from test_screenshot_runtime import Machine


class Operation025(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT/'work/pkg').exists():raise unittest.SkipTest('Local source assets unavailable')
        cls.b=Build(DEFAULT_FONT)
        cls.originals=[]
        for path in sorted((ROOT/'work/story').glob('*.lua')):
            raw=path.read_bytes()
            if b'OPERATE_TBL' not in raw:continue
            asset=path.relative_to(ROOT).as_posix()
            built=cls.b.lua(raw,asset,path.stem)
            cls.originals.append((raw,built))

    def test_numbered_screenshot_conditions_resolve_through_both_draw_paths(self):
        for jp,en in [('敵の全滅。','Defeat all enemies.'),
                      ('いずれかの味方ユニットの撃墜。','Any allied unit is defeated.')]:
            for prefix in O.NUMBERS:
                source=(prefix+jp).encode('cp932');target=self.b.codec.encode(prefix+en)
                self.assertEqual(self.b.operation_hooks[source],target)
                for method in ('draw','converted'):
                    m=Machine(self.b.codec,self.b.operation_hooks)
                    if method=='converted':m.put(m.state+0xb8,source+b'\0')
                    m.run(method,source)
                    self.assertEqual(m.cstr(m.r[31 if method=='converted' else 3]),target)
                    before,fp,cr,lr=m.initial
                    if method=='draw':
                        # The displaced native cmpwi r7,0 intentionally sets CR7.
                        self.assertEqual(m.cr,(cr&~15)|4)
                        self.assertEqual(m.lr,lr)
                    else:
                        self.assertEqual(m.cr,cr)
                    self.assertEqual(m.f,fp)

    def test_all_conditions_have_exact_native_generated_variants_and_fit(self):
        self.assertEqual(len(self.b.operation_report),72)
        for row in self.b.operation_report:
            self.assertEqual(row['numbered_variants'],3)
            self.assertEqual(row['display_lines'],len(row['display'].split('\n')))
            self.assertLessEqual(max(row['line_widths']),O.WIDTH)
            for fragment in row['formatted']:
                self.assertEqual(self.b.operation_hooks[fragment['source'].encode('cp932')],
                                 self.b.codec.encode(fragment['display']))
                self.assertLessEqual(max(fragment['line_widths']),O.WIDTH)
        continuations=[f for r in self.b.operation_report for f in r['formatted'] if f['source'].startswith(O.INDENT)]
        self.assertTrue(continuations)
        f=continuations[0];m=Machine(self.b.codec,self.b.operation_hooks)
        m.run('draw',f['source'].encode('cp932'))
        self.assertEqual(m.cstr(m.r[3]),self.b.codec.encode(f['display']))

    def test_bounded_native_tables_unchanged_and_unrelated_text_not_matched(self):
        pattern=rb'OPERATE_TBL\s*=\s*\{\s*str_tbl\s*=\s*\{(.*?)\}\s*;'
        for before,after in self.originals:
            self.assertEqual(re.search(pattern,before,re.S)[1],re.search(pattern,after,re.S)[1])
        m=Machine(self.b.codec,self.b.operation_hooks)
        key='１．これは条件ではない。'.encode('cp932')
        m.run('draw',key)
        self.assertEqual(m.cstr(m.r[3]),key)
        O.guard(self.b.original_elf)
        bad=bytearray(self.b.original_elf);bad[O.FORMATTER[0]-0x10000]^=1
        with self.assertRaises(ValueError):O.guard(bytes(bad))

    def test_elgan_resolves_to_requested_spelling_and_old_build_missing_numbered_key(self):
        line=self.b.story['rengoku:STGZ3REN_00004:00011']
        self.assertIn('Roddick',line);self.assertNotIn('Rhodic',line)
        previous=ROOT/'work/builds/rengoku_en_024/intermediate/EBOOT.ELF'
        if previous.exists():
            self.assertNotIn('１．敵の全滅。'.encode('cp932')+b'\0',previous.read_bytes())
        self.assertIn('１．敵の全滅。'.encode('cp932'),self.b.operation_hooks)


if __name__=='__main__':unittest.main()
