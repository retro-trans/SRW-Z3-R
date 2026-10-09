"""Source-backed regressions for narration, vertical terrain and chapter art."""
import json
from pathlib import Path
import struct
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_game import Build
import rengoku_runtime as R
import rengoku_narration as N
import rengoku_chapter_art as A
import rengoku_screenshot_layout as L
from test_screenshot_runtime import Machine


class Layout006(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT/'work/pkg').exists():raise unittest.SkipTest('Local original assets unavailable')
        cls.build=Build(R.DEFAULT_FONT)

    def test_all_vertical_terrain_occurrences_keep_native_cell_and_line_counts(self):
        b=self.build;jp='空\n陸\n海\n宇'
        rows=[r for r in b.occ.values() if r['jp']==jp]
        self.assertEqual(len(rows),22)
        expected=b.codec.encode('\ue100\n\ue101\n\ue102\n\ue103')
        self.assertEqual([len(s) for s in expected.split(b'\n')],[2]*4)
        key=next(r['asset'] for r in rows if r['asset'].endswith('AIDDATAPACK_R.CPK:0'))
        raw=b.asset(key);out=b.fssa(raw,b.byasset[key]);base=struct.unpack_from('>I',raw,32)[0]
        start,end=struct.unpack_from('>II',raw,0x48);found=0
        for p in range(start,end,32):
            q=base+struct.unpack_from('>I',raw,p)[0]
            if raw[q:raw.index(0,q)]!=jp.encode('cp932'):continue
            target=base+struct.unpack_from('>I',out,p)[0]
            self.assertEqual(out[target:out.index(0,target)],expected)
            self.assertEqual(out[p+4:p+32],raw[p+4:p+32]);found+=1
        self.assertGreater(found,0)
        m=Machine(b.codec,L.hooks(b.codec,b.locale['messages']))
        m.run('draw',jp.encode('cp932'));self.assertEqual(m.cstr(m.r[3]),expected)
        self.assertEqual(L.text_for_field('空の世界','Sky world'),'Sky world')

    def test_narration_all_32_rows_fit_without_changing_cues_or_word_stream(self):
        b=self.build;total=0
        for mid in (13,14):
            key='work/pkg/USRDIR/DATA_REN/AIDDATA/AIDDATAPACK_R.CPK:'+str(mid)
            raw=b.asset(key);out,hooks,proof=N.apply(raw,b.byasset[key],b.codec,mid)
            self.assertEqual(out[20:],raw[20:]);self.assertEqual(out[7:9],raw[7:9])
            self.assertEqual(out[:4],raw[:4]);self.assertEqual(out[10:20],raw[10:20])
            self.assertEqual(out[4:7],bytes((32,36,32)));self.assertEqual(out[9],96)
            for row in proof['rows']:
                self.assertLessEqual(row['width'],1088);self.assertNotIn('\n',row['display'])
            rows={r['offset']:r for r in b.byasset[key]};stride=raw[2]+30
            for a,z in N.GROUPS[mid]:
                before=' '.join(rows[20+i*stride]['english'] for i in range(a,z)).split()
                after=' '.join(r['display'] for r in proof['rows'] if a<=r['row']<z).split()
                self.assertEqual(before,after)
            self.assertEqual(len(hooks),len(proof['rows']));total+=len(hooks)
            m=Machine(b.codec,hooks);jp=next(iter(hooks));m.run('draw',jp)
            self.assertEqual(m.cstr(m.r[3]),hooks[jp])
        self.assertEqual(total,32)

    def test_narration_source_guards_and_rengoku_renderer_fields(self):
        b=self.build;raw=b.original_elf
        # Header loads and setter independently located in this game's ELF.
        self.assertEqual(raw[0x48e28:0x48e3c].hex(),'813e03d489690004890900078809000689490005')
        self.assertEqual(raw[0x48f4c:0x48f50].hex(),'88a90009')
        key='work/pkg/USRDIR/DATA_REN/AIDDATA/AIDDATAPACK_R.CPK:13'
        source=bytearray(b.asset(key));source[7]=59
        with self.assertRaises(ValueError):N.apply(bytes(source),b.byasset[key],b.codec,13)

    def test_all_15_title_textures_preserve_headers_and_have_two_visible_copies(self):
        b=self.build;rows=A.catalog();self.assertEqual(set(rows),set(range(4,19)))
        for mid,row in rows.items():
            raw=b.asset(row['asset']);out=A.title_apply(raw,row,b.font)
            off,size=struct.unpack_from('>II',raw,16)
            self.assertEqual(raw[:off],out[:off]);self.assertEqual(raw[off+size:],out[off+size:])
            self.assertEqual(len(raw),len(out));self.assertNotEqual(raw,out)
            im=A.title_image(row['english'],b.font)
            for y in (0,128):
                box=im.crop((0,y,1536,y+128)).getbbox();self.assertIsNotNone(box)
                self.assertGreater(box[0],100);self.assertLess(box[2],1436)

    def test_every_single_and_double_digit_header_quad_and_unrelated_bytes(self):
        b=self.build
        for mid in (100,101):
            raw=b.asset('work/pkg/'+A.EFF+':'+str(mid))
            out,counts=A.effect_apply(raw,mid,b.font,'Green Earth');g=A.EFFECTS[mid][0]
            edits,_=A.geometry(raw,mid);expected=bytearray(raw[:g])
            for p,v in edits:expected[p:p+len(v)]=v
            self.assertEqual(bytes(expected),out[:g])
            # Independent geometry walk: all first glyphs expanded; each digit
            # shifts exactly +128; all old suffix vertex alphas become zero.
            counted=[0,0,0]
            for p in range(40,g-16,2):
                z,x,y,w,h,flags,mode,tex=struct.unpack_from('>8H',raw,p)
                if z or flags!=0x5000 or mode not in (0x101,0x201):continue
                before=struct.unpack_from('>8h',raw,p-16);after=struct.unpack_from('>8h',out,p-16)
                if tex==2 and y==0 and w==144 and h==112:
                    if x in (0,288):
                        self.assertEqual(after[2]-before[2],128);counted[0]+=1
                    elif x in (144,432):self.assertEqual(out[p-40:p-24],bytes(16));counted[2]+=1
                elif tex in ((4,) if mid==100 else (4,5)) and x==0 and y in (0,112) and w==96 and h==112:
                    self.assertEqual(tuple(v-u for u,v in zip(before,after)),(128,0,128,0,128,0,128,0));counted[1]+=1
            self.assertEqual(counted,counts)
            # Each texture except edited 2/3 is byte-identical, including digits.
            for i in range(struct.unpack_from('>I',raw,g+8)[0]):
                if i in (2,3):continue
                off,size=struct.unpack_from('>II',raw,g+16+36*i)
                self.assertEqual(out[g+off:g+off+size],raw[g+off:g+off+size])

    def test_final_episode_only_changes_header_and_title_rectangles(self):
        b=self.build;raw=b.asset('work/pkg/'+A.EFF+':102');g=A.EFFECTS[102][0]
        out,_=A.effect_apply(raw,102,b.font,A.catalog()[18]['english'])
        off,size=struct.unpack_from('>II',raw,g+16+36*2);off+=g
        self.assertEqual(out[:off],raw[:off]);self.assertEqual(out[off+size:],raw[off+size:])
        # Preserve the English Epilogue/Another story/logo and unused cells.
        for y in range(800):
            for x0,x1 in ((0,592),) if y<224 else (((0,1024),) if y<544 else ()):
                a=off+(y*1024+x0)*4;z=off+(y*1024+x1)*4
                self.assertEqual(out[a:z],raw[a:z])
        for y in (0,112,544,672):
            a=off+y*1024*4;self.assertNotEqual(out[a:a+112*4096],raw[a:a+112*4096])


if __name__=='__main__':unittest.main()
