"""Regressions for the actual source records shown in the user's screenshots."""
import importlib.util
import json
from pathlib import Path
import struct
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from cpk import CPK
import rengoku_runtime as R
import rengoku_screenshot_layout as L
from test_screenshot_runtime import Machine


class Layout005(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not R.DEFAULT_FONT.exists():raise unittest.SkipTest('Local font unavailable')
        cls.codec=R.Codec([''.join(chr(c) for c in range(32,127))],
                        {1:bytes(128+4096*1120*2),3:bytes(128+4096*1120*2)},R.DEFAULT_FONT)
        cls.messages={str(i):{'source':jp,'text':en} for i,(jp,en) in enumerate(
            [('底力','Potential'),('援護攻撃','Support Atk'),('援護防御','Support Def')])}

    def source_layout(self):
        path=ROOT/'work/pkg/USRDIR/DATA_REN/AIDDATA/AIDDATAPACK_R.CPK'
        if not path.exists():self.skipTest('Original local FSSA unavailable')
        c=CPK(str(path));raw=c.read(next(e for e in c.files if e['id']==0))
        return raw,L.apply_fssa(raw,raw,self.codec)[0]

    def field(self,raw,p):
        base=struct.unpack_from('>I',raw,32)[0]
        q=base+struct.unpack_from('>I',raw,p)[0]
        return raw[q:raw.index(0,q)]

    def test_four_actual_ace_fragments_become_one_heading(self):
        raw,out=self.source_layout()
        self.assertEqual(self.field(out,0x8a664),self.codec.encode('Ace Bonus'))
        for p in (0x8a684,0x8a6a4,0x8a6c4):self.assertEqual(self.field(out,p),b'')
        # Other unrelated bonus fragments must retain their original text.
        self.assertEqual(self.field(out,0x8a464),self.field(raw,0x8a464))

    def test_panel_bounds_and_suffix_geometry(self):
        raw,out=self.source_layout()
        for p,en in ((0x9d784,'Spirits'),(0x9d5c4,'Foc'),(0x9dd64,'Foc')):
            self.assertEqual(self.field(out,p),self.codec.encode(en))
        self.assertLess(L.line_width(self.codec,'Spirits',28),200)
        for p in (0x9cc84,0x9cea4,0x9cf24):
            self.assertEqual(out[p+4:p+12],raw[p+4:p+12])
            self.assertEqual(out[p+18],raw[p+18])
            self.assertLess(415.5+L.line_width(self.codec,'Nick',out[p+19]),475)
        self.assertEqual(out[0x8f044+18:0x8f044+20],bytes((31,31)))
        self.assertAlmostEqual(640+640*struct.unpack_from('>f',out,0x8f048)[0],825.5,places=4)

    def test_terrain_physical_fields_and_normal_stat_font(self):
        for jp in ('空','陸','海','宇','空陸海宇','空陸水地'):
            target=L.text_for_field(jp,'uncompressed words')
            self.assertEqual(len(self.codec.encode(target)),len(jp)*2)
        hooks=L.hooks(self.codec,self.messages)
        for jp,en in (('格闘','MEL'),('射撃','RNG')):
            self.assertEqual(hooks[jp.encode('cp932')],self.codec.encode(en))
            self.assertEqual(len(hooks[jp.encode('cp932')]),6)
            m=Machine(self.codec,hooks)
            m.put(m.state+0xb8,jp.encode('cp932')+b'\0')
            m.run('converted',b'ignored')
            self.assertEqual(m.cstr(m.r[31]),self.codec.encode(en))
            self.assertLess(L.line_width(self.codec,en,28),64)

    def test_compact_rasters_match_z31_terrain_recipe(self):
        path=ROOT.parent/'SRW Z3/tools/ttfglyph.py'
        if not path.exists():self.skipTest('Read-only reference unavailable')
        spec=importlib.util.spec_from_file_location('reference_face',str(path))
        ref=importlib.util.module_from_spec(spec)
        old_bytecode=sys.dont_write_bytecode;sys.dont_write_bytecode=True
        sys.path.insert(0,str(path.parent))
        try:spec.loader.exec_module(ref)
        finally:sys.path.pop(0);sys.dont_write_bytecode=old_bytecode
        face=ref.Face(str(R.DEFAULT_FONT),11,20,0,0.3)
        for word in ('Air','Grd','Wtr','Spc','Und'):
            parts=[face.natural(c) for c in word];x=(32-sum(p[3] for p in parts))/2
            cov=bytearray(1024)
            for im,l,t,adv in parts:
                face._blit(cov,im,x+l,20+t);x+=adv
            self.assertEqual(R.rodin_compact(R.DEFAULT_FONT,word).tobytes(),bytes(cov),word)

    def test_native_movement_fields_and_stat_sources(self):
        path=ROOT/'work/eboot/EBOOT.ELF'
        if not path.exists():self.skipTest('Original local ELF unavailable')
        raw=path.read_bytes();out=bytearray(raw)
        for off,old,new,_ in L.native_movement_fields(raw,self.codec):
            self.assertEqual(len(old),len(new));out[off:off+len(new)]=new
        for p in (0x888e50,0x888e58,0x888ef0,0x888ef8):self.assertEqual(out[p:p+8],raw[p:p+8])
        for base in (0x888ec8,0x889128):
            for i,jp in enumerate('空陸水地'):
                self.assertEqual(out[base+i*8:base+i*8+4],self.codec.encode(L.TERRAIN[jp],utf8=True)+b'\0')

    def test_library_wrap_preserves_prose_and_blank_lines(self):
        text=("Deputy commander of the Chrono Reformists' field unit.\n"
              "He serves as Advent's right-hand man and works tirelessly to live up to his expectations.\n"
              "Intelligent and sensible, he also possesses the strength of mind to remain calm in any situation.\n"
              "His cooking skills are on a professional level.")
        for tag in ('DSCR','DSC2'):
            out=L.library_text(self.codec,tag,text)
            self.assertEqual(out.split(),text.split())
            self.assertGreater(len(out.splitlines()),len(text.splitlines()))
            self.assertLessEqual(max(L.line_width(self.codec,s) for s in out.splitlines()),1140)
            self.assertIn('\n\n',L.library_text(self.codec,tag,text+'\n\nSecond paragraph.'))
        self.assertEqual(L.library_text(self.codec,'NAME',text),text)

    def test_complete_chapter_heading_in_both_draw_paths(self):
        source=json.loads((ROOT/'source/non_dialogue.json').read_text(encoding='utf8'))['records']
        rows=[dict(r,english='Green Earth') for r in source]
        hooks=L.chapter_hooks(self.codec,rows)
        jp='第１話『翠の地球』'
        self.assertEqual(hooks[jp.encode('cp932')],self.codec.encode('Episode 1: Green Earth'))
        for method in ('draw','converted'):
            m=Machine(self.codec,hooks)
            if method=='converted':m.put(m.state+0xb8,jp.encode('cp932')+b'\0')
            m.run(method,jp.encode('cp932'))
            self.assertEqual(m.cstr(m.r[31 if method=='converted' else 3]),self.codec.encode('Episode 1: Green Earth'))
        self.assertNotIn('第１話『未知』'.encode('cp932'),hooks)


if __name__=='__main__':unittest.main()
