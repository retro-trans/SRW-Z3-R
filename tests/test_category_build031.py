"""Source-bound screenshot category checks and execution of emitted PPC lookup."""
import json
from pathlib import Path
import struct
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_game import Build,DEFAULT_FONT
from test_link_runtime import CPU
import rengoku_bonus_runtime as G
import rengoku_carryover_layout as C
import rengoku_operation_layout as O
from rengoku_runtime import patch_elf
from rengoku_search_layout import field
from rengoku_screenshot_layout import line_width

ASSET='work/pkg/USRDIR/DATA_REN/AIDDATA/AIDDATAPACK_R.CPK'

class Categories031(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=Build(DEFAULT_FONT)
        cls.raw=cls.b.asset(ASSET+':0')
        cls.fssa=cls.b.fssa(cls.raw,cls.b.byasset[ASSET+':0'])
        cls.stage=ROOT/'work/story/STGZ3REN_00099.lua'
        cls.before=cls.stage.read_bytes()
        cls.after=cls.b.lua(cls.before,'work/story/'+cls.stage.name,cls.stage.stem)
        cls.elf,cls.runtime=patch_elf(cls.b.original_elf,cls.b.codec,
                                     {**cls.b.hooks,**cls.b.operation_hooks},cls.b.elf_edits)

    def lookup(self,text):
        raw=text.encode('cp932') if isinstance(text,str) else text
        c=CPU(self.elf);src=0x1800000;c.put(src,raw+b'\0'+bytes(8))
        c.put(G.BUFFER-8,b'CANARY00'+bytes([0xa5])*G.CAPACITY+b'CANARY11')
        c.r[3]=src;c.cr=[1,-1,0,1,-1,0,1,-1]
        regs=list(c.r);cr=list(c.cr);lr=c.lr;fp=list(c.f)
        c.run(self.runtime['stubs']['lookup'],{lr})
        for i in range(32):
            if i!=3:self.assertEqual(c.r[i],regs[i],('register',i))
        self.assertEqual(c.cr,cr);self.assertEqual(c.lr,lr);self.assertEqual(c.f,fp)
        self.assertEqual(c.read(src,len(raw)+1),raw+b'\0')
        self.assertEqual(c.read(G.BUFFER-8,8),b'CANARY00')
        self.assertEqual(c.read(G.BUFFER+G.CAPACITY,8),b'CANARY11')
        return c.string(c.r[3]),c.r[3],src

    def test_generated_bonus_families_and_existing_level_forms(self):
        families={}
        for key,value in self.b.hooks.items():
            try:jp=key.decode('cp932')
            except UnicodeDecodeError:continue
            if jp.endswith('＋１') and jp[:-2].encode('cp932') in self.b.hooks:
                name=jp[:-2]
                if name!=name.strip():continue
                if (name+'Ｌ１').encode('cp932') in self.b.hooks:families[name]=value
        self.assertGreaterEqual(len(families),13)
        for jp,first in families.items():
            base=self.b.hooks[jp.encode('cp932')]
            for n in range(1,10):
                want=base+self.b.codec.encode(' +'+str(n))
                for left in ('',' ','　'):
                    for right in ('',' ','　'):
                        for plus in ('+','＋'):
                            for digit in (str(n),chr(0xff10+n)):
                                self.assertEqual(self.b.hooks[(jp+left+plus+right+digit).encode('cp932')],want,jp)
            self.assertIn((jp+'Ｌ１＋２').encode('cp932'),self.b.hooks)
        for jp,en in [('サイズ差補正無視＋１','Ignore Size +1'),
                      ('サイズ差補正無視＋２','Ignore Size +2'),
                      ('援護攻撃＋２','Support Atk +2'),('援護防御＋２','Support Def +2')]:
            actual,ptr,src=self.lookup(jp)
            self.assertEqual(actual,self.b.codec.encode(en));self.assertNotEqual(ptr,src)
            self.assertLessEqual(line_width(self.b.codec,en,28),330)

    def test_gold_all_generated_amounts_and_bounds(self):
        cases=[('','Gold '),('３００００','Gold Bar 30000'),('0','Gold Bar 0'),
               ('０００１０','Gold Bar 00010'),('１２3 ４　5','Gold Bar 12345'),
               ('12345678','Gold Bar 12345678'),('123456789','Gold 123456789'),
               ('4294967295','Gold 4294967295'),('０１２３４５６７８９','Gold 0123456789')]
        for tail,en in cases:
            actual,ptr,src=self.lookup('金塊　'+tail)
            self.assertEqual(actual,self.b.codec.encode(en));self.assertEqual(ptr,G.BUFFER)
            self.assertLess(len(actual)+1,G.CAPACITY)
            self.assertLessEqual(line_width(self.b.codec,en,32),330)
        self.assertLessEqual(line_width(self.b.codec,'Gold ',32),84)
        for tail in ('12345678901','３００００G','-1','あ',' '*65):
            raw=('金塊　'+tail).encode('cp932');actual,ptr,src=self.lookup(raw)
            self.assertEqual(actual,raw);self.assertEqual(ptr,src)
        actual,ptr,src=self.lookup('Unrelated reward');self.assertEqual(ptr,src)
        G.guard(self.b.original_elf)
        bad=bytearray(self.b.original_elf);bad[0x95f34c]^=1
        with self.assertRaises(ValueError):G.guard(bad)

    def test_both_carryover_variants_keep_live_values_and_separate_columns(self):
        for row in (0x9a244,0x9a324):
            self.assertEqual(field(self.raw,row),field(self.fssa,row))
            self.assertEqual(self.raw[row:row+4],self.fssa[row:row+4])
            self.assertEqual(self.raw[row+8:row+32],self.fssa[row+8:row+32])
            self.assertAlmostEqual(struct.unpack_from('>f',self.fssa,row+4)[0],(760-640)/640)
        for row in self.b.carryover_report:
            if row.get('live_values_preserved'):self.assertGreater(row['gap'],130)
            else:
                self.assertEqual(field(self.fssa,int(row['row'],16)),self.b.codec.encode(row['display']))
                self.assertLessEqual(max(row['line_widths']),row['width_limit'])
        for row in (0x9a204,0x9a284,0x9a2c4,0x9a364):self.assertEqual(field(self.fssa,row),b'')
        self.assertEqual(field(self.fssa,0x9a224),field(self.fssa,0x9a304))
        self.assertEqual(field(self.fssa,0x9a264),field(self.fssa,0x9a344))
        self.assertIn(self.b.codec.encode(C.UPGRADE),field(self.fssa,0x9a2a4))
        self.assertNotIn('Z Chips',C.NO_Z+C.NO_Z_RATES)
        self.assertIn('Z Chips',C.INTRO);self.assertIn('Z Chips',C.RATES)

    def test_indexed_no_z_compact_prose_round_trips(self):
        raw=self.b.asset(ASSET+':5');out=self.b.indexed(raw,self.b.byasset[ASSET+':5'])
        size=struct.unpack_from('>I',out,24)[0];base=32+size+16
        for i,en in ((164,C.NO_Z),(165,C.NO_Z_RATES)):
            p=base+struct.unpack_from('>I',out,32+i*4)[0]
            self.assertEqual(out[p:out.index(0,p)],self.b.codec.encode(en))

    def test_final_sr_raw_escape_stays_native_and_runtime_form_resolves(self):
        raw='このシナリオにはＳＲポ\\イントはありません。'.encode('cp932')
        self.assertIn(raw,self.before);self.assertIn(raw,self.after)
        jp=raw.decode('cp932').replace('\\イ','イ')
        for prefix in ('',)+O.NUMBERS:
            actual,ptr,src=self.lookup(prefix+jp)
            self.assertEqual(actual,self.b.codec.encode(prefix+'There are no SR Points in this scenario.'))
            self.assertNotEqual(ptr,src)
        proof=[r for r in self.b.operation_report if r.get('raw_source_escape_alias')]
        self.assertEqual(len(proof),1)

if __name__=='__main__':unittest.main()
