"""Regression checks against actual NPJB00689 data and measured text bounds."""
from pathlib import Path
import sys
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_game import Build
from rengoku_runtime import DEFAULT_FONT
from rengoku_search_layout import FSSA_ASSET,RPW_ASSET,field,effect_hooks
from rengoku_screenshot_layout import hooks,line_width
import rengoku_category_layout as C
from test_screenshot_runtime import Machine


class Category019(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT/'work/pkg').exists():raise unittest.SkipTest('Local source unavailable')
        cls.b=Build(DEFAULT_FONT)

    def test_generated_skill_levels_and_bonus_suffixes_are_translated(self):
        h=hooks(self.b.codec,self.b.locale['messages'])
        for jp,en in [('サイズ差補正無視','Ignore Size'),('指揮官','Commander'),
                      ('ニュータイプ','Newtype'),('シールド防御','Shield Defense')]:
            for n in range(1,10):
                self.assertEqual(h[(jp+'Ｌ'+chr(0xff10+n)).encode('cp932')],
                                 self.b.codec.encode(en+' L'+str(n)))
                for bonus in range(1,10):
                    self.assertEqual(h[(jp+'Ｌ'+chr(0xff10+n)+'＋'+chr(0xff10+bonus)).encode('cp932')],
                                     self.b.codec.encode(en+' L%d+%d'%(n,bonus)))

    def test_every_skill_and_spirit_description_fits_its_panel(self):
        _,report=effect_hooks(self.b.asset(RPW_ASSET),self.b.byasset[RPW_ASSET],self.b.codec)
        self.assertEqual(report['bindings'],204)
        for r in report['rows']:
            self.assertLessEqual(len(r['display'].split('\n')),r['max_lines'])
            self.assertLessEqual(max(r['line_widths']),r['width_limit'])
            if r['family']=='sk-pri':self.assertEqual((r['width_limit'],r['glyph_quad']),(760,32))

    def test_popup_variants_join_header_and_remove_only_placeholder(self):
        raw=self.b.asset(FSSA_ASSET);built=self.b.fssa(raw,self.b.byasset[FSSA_ASSET])
        for row in (0x8bec4,0x99864,0x8bf04,0x9a024):self.assertEqual(field(built,row),b'')
        for row in (0x8bee4,0x9a004):
            self.assertEqual(field(built,row),self.b.codec.encode('Custom Bonus obtained.'))
            self.assertEqual(raw[row+4:row+19],built[row+4:row+19])
        for r in self.b.category_bonus_report:self.assertLessEqual(r['width'],r['limit'])
        with self.assertRaises(ValueError):C.apply_fssa(bytes([raw[0]^1])+raw[1:0x8bea4]+b'\xff'*4+raw[0x8bea8:],built,self.b.codec)

    def test_operations_keep_original_native_text_before_draw_lookup(self):
        asset='work/story/STGZ3REN_00043.lua';raw=(ROOT/asset).read_bytes()
        built=self.b.lua(raw,asset,'STGZ3REN_00043')
        def native_block(data):
            return re.search(rb'OPERATE_TBL\s*=\s*\{\s*str_tbl\s*=\s*\{(.*?)\}\s*;',data,re.S)[1]
        self.assertEqual(native_block(raw),native_block(built))
        jp='勝利条件達成時までに敵を全滅させる。'
        en='Defeat all enemies before fulfilling the victory condition.'
        self.assertEqual(self.b.operation_hooks[jp.encode('cp932')],self.b.codec.encode(en))
        self.assertGreater(len(self.b.codec.encode(en)),len(jp.encode('cp932')))
        for method in ('draw','converted'):
            machine=Machine(self.b.codec,self.b.operation_hooks)
            key=jp.encode('cp932')
            if method=='converted':machine.put(machine.state+0xb8,key+b'\0')
            machine.run(method,key)
            self.assertEqual(machine.cstr(machine.r[31 if method=='converted' else 3]),self.b.codec.encode(en))
        self.assertTrue(all(max(r['line_widths'])<=950 for r in self.b.operation_report))

    def test_all_dialogue_rows_fit_three_measured_lines(self):
        for identity,text in self.b.story.items():
            if not self.b.story_rows[identity]['pid']:continue
            lines=text.split('\n')[1:]
            self.assertLessEqual(len(lines),3,identity)
            self.assertLessEqual(max(line_width(self.b.codec,s,32) for s in lines),870,identity)

    def test_complete_bonus_category_fits(self):
        _,rows=C.bonus_hooks(self.b.occ.values(),self.b.codec)
        self.assertGreaterEqual(len(rows),8)
        for r in rows:self.assertLessEqual(max(r['line_widths']),1070)


if __name__=='__main__':unittest.main()
