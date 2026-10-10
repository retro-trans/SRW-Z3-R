"""Actual Rengoku upgrade/credit fields and complete linked story regressions."""
import re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from build_game import Build
from rengoku_runtime import DEFAULT_FONT
from rengoku_search_layout import FSSA_ASSET,field
from rengoku_screenshot_layout import line_width
from rengoku_category_layout import wrap
from test_screenshot_runtime import Machine
import rengoku_credits_layout as C
import rengoku_upgrade_selector as U


class Category022(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.b=Build(DEFAULT_FONT)

    def test_upgrade_selector_labels_fit_and_live_styles_stay_native(self):
        raw=self.b.asset(FSSA_ASSET);out=self.b.fssa(raw,self.b.byasset[FSSA_ASSET])
        for p,(jp,en,limit) in U.LABELS.items():
            self.assertEqual(field(out,p),self.b.codec.encode(en))
            self.assertEqual(raw[p+4:p+32],out[p+4:p+32])
            self.assertTrue(all(line_width(self.b.codec,s,raw[p+19])<=limit for s in en.split('\n')))
        self.assertEqual(raw[0x9a0a4+4:0x9a0a4+32],out[0x9a0a4+4:0x9a0a4+32])
        self.assertEqual(field(out,0x9a0a4),self.b.codec.encode('Halved'))
        bad=bytearray(raw);bad[0x9a044:0x9a048]=b'\xff'*4
        with self.assertRaises((ValueError,IndexError)):U.apply(bytes(bad),out,self.b.codec)

    def test_every_credit_row_fits_and_preserves_scroll_commands(self):
        asset='work/pkg/USRDIR/DATA_REN/AIDDATA/AIDDATAPACK_R.CPK:15'
        raw=self.b.asset(asset);out=self.b.credits(raw,self.b.byasset[asset]);proof=self.b.credit_layout_report
        self.assertEqual(len(proof['rows']),333)
        self.assertEqual(out[20:],raw[20:])
        self.assertTrue(all(a==b or i in (4,6) for i,(a,b) in enumerate(zip(raw,out))))
        self.assertEqual(proof['quad'],32)
        byoffset={r['offset']:r for r in self.b.byasset[asset]}
        for r in proof['rows']:
            self.assertLessEqual(r['width'],1120)
            self.assertEqual(r['display'].split(),byoffset[r['offset']]['english'].split())
        for name in ('Yohei Azakami','Yusuke Handa'):
            row=next(r for r in proof['rows'] if name in r['display'])
            prefix=row['display'].split(name)[0]
            self.assertLessEqual(abs(64+line_width(self.b.codec,prefix,32)-704),4)
            key=byoffset[row['offset']]['jp'].encode('cp932')
            for method in ('draw','converted'):
                machine=Machine(self.b.codec,self.b.credit_hooks)
                if method=='converted':machine.put(machine.state+0xb8,key+b'\0')
                machine.run(method,key)
                self.assertEqual(machine.cstr(machine.r[31 if method=='converted' else 3]),
                                 self.b.codec.encode(row['display']))
        bad=bytearray(raw);bad[4]^=1
        with self.assertRaises(ValueError):C.apply(bytes(bad),self.b.byasset[asset],self.b.codec)

    def test_all_keyword_edges_and_ending_dialogue_are_complete(self):
        for identity,text in self.b.story.items():
            self.assertIsNone(re.search(r'[A-Za-z0-9]《|》[A-Za-z0-9]',text),identity)
        for n in (68,75):
            self.assertIn('with 《Aim》',self.b.story['rengoku:STGZ3REN_00092:%05d'%n])
        en=self.b.story['rengoku:STGZ3REN_00107:00045']
        self.assertIn('travel between this Earth and the other one',en)
        self.assertIn('should become possible',en)
        self.assertLessEqual(len(en.split('\n')[1:]),3)
        self.assertLessEqual(max(line_width(self.b.codec,s,32) for s in en.split('\n')[1:]),870)

    def test_episode13_condition_is_complete_in_owned_display_storage(self):
        asset='work/story/STGZ3REN_00079.lua';raw=(ROOT/asset).read_bytes()
        out=self.b.lua(raw,asset,'STGZ3REN_00079')
        pattern=rb'OPERATE_TBL\s*=\s*\{\s*str_tbl\s*=\s*\{(.*?)\}\s*;'
        self.assertEqual(re.search(pattern,raw,re.S)[1],re.search(pattern,out,re.S)[1])
        jp='味方ユニットのいずれかに敵を７機以上、撃墜させる。'.encode('cp932')
        en='Have any one allied unit defeat at least 7 enemies.'
        self.assertEqual(self.b.operation_hooks[jp],self.b.codec.encode(wrap(self.b.codec,en,950)))
        machine=Machine(self.b.codec,self.b.operation_hooks);machine.run('draw',jp)
        self.assertEqual(machine.cstr(machine.r[3]),self.b.codec.encode(en))


if __name__=='__main__':unittest.main()
