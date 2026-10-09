"""Build safety and format regression checks; no game outputs are written."""
import json
from pathlib import Path
import struct
import sys
import unittest
from types import SimpleNamespace

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_game import Build, ROOT, checked_output, patch_sfo
from rengoku_runtime import Codec, TEXT, branch, build_hook_table, cell, patch_elf


class BuildSafety(unittest.TestCase):
    def test_output_cannot_be_source_or_existing_directory(self):
        for path in (ROOT/'work/pkg',ROOT/'work/builds',ROOT.parent/'SRW Z3/work/output',ROOT):
            with self.assertRaises(ValueError):checked_output(path)

    def test_branch_signed_range_and_alignment(self):
        self.assertEqual(branch(0x14158,0x8fb500)&3,0)
        self.assertEqual(branch(0x147dc,0x8fb600,True)&3,1)
        for target in (0x4000000,0x10003,-0x4000000):
            with self.assertRaises(ValueError):branch(0x10000,target)

    def test_other_game_executable_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'Wrong Rengoku ELF'):
            patch_elf(b'not the authenticated NPJB00689 executable',None,{})

    def test_hook_bucket_collision_and_single_byte_key(self):
        pairs={b'abc':b'English A',b'abd':b'English B',b'x':b'X'}
        data=build_hook_table(pairs)
        for source,want in pairs.items():
            bucket=(source[0]<<8)|(source[1] if len(source)>1 else 0)
            pos=struct.unpack_from('>I',data,bucket*4)[0]-TEXT
            found=None
            while True:
                jp,en=struct.unpack_from('>II',data,pos)
                if not jp:break
                jp-=TEXT;en-=TEXT
                if data[jp:data.index(0,jp)]==source:found=data[en:data.index(0,en)]
                pos+=8
            self.assertEqual(found,want)
        with self.assertRaises(ValueError):build_hook_table({b'a\0b':b'English'})

    def test_real_elf_keeps_native_loads_tls_and_section_alignment(self):
        source=ROOT/'work/eboot/EBOOT.ELF'
        if not source.exists():self.skipTest('Ignored source executable not present')
        before=source.read_bytes()
        after,report=patch_elf(before,SimpleNamespace(widths={},codes={},unicode={}),{b'abc':b'xyz'})
        ph=struct.unpack_from('>Q',before,32)[0]
        old=[struct.unpack_from('>IIQQQQQQ',before,ph+i*56) for i in range(8)]
        new=[struct.unpack_from('>IIQQQQQQ',after,ph+i*56) for i in range(8)]
        self.assertEqual(sum(r[0]==1 and bool(r[6]) for r in new),2)
        self.assertEqual(old[5:],new[5:])
        self.assertEqual(before[24:32],after[24:32])
        oldsh=struct.unpack_from('>Q',before,40)[0];newsh=struct.unpack_from('>Q',after,40)[0]
        self.assertEqual(newsh%8,oldsh%8)
        count=struct.unpack_from('>H',before,60)[0]
        for i in range(count):
            a=struct.unpack_from('>IIQQQQIIQQ',before,oldsh+i*64)
            b=struct.unpack_from('>IIQQQQIIQQ',after,newsh+i*64)
            if a[8] and a[1]!=8:self.assertEqual(a[4]%a[8],b[4]%b[8])
        self.assertTrue(report['original_bss_zero_filled'])


class CodecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        font=Path('C:/Windows/Fonts/arial.ttf')
        if not font.exists():raise unittest.SkipTest('Local build font unavailable')
        blank=bytes(128+4096*1120*2)
        cls.codec=Codec(['ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 $%+-\\'],{1:blank,3:blank},font)

    def test_native_space_and_assigned_codes_are_not_allocated(self):
        self.assertNotIn(0x8140,self.codec.codes.values())
        for code in self.codec.codes.values():
            with self.assertRaises(UnicodeDecodeError):struct.pack('>H',code).decode('cp932')

    def test_runtime_placeholders_survive_verbatim(self):
        for value in ('$n','$l','%03d','%.2f','%s','%%','\\n','【必要容量】','【セーブデータ】'):
            self.assertEqual(self.codec.encode(value),value.encode('cp932'))
        self.assertEqual(self.codec.encode('\x02'),b'\x02')

    def test_quotes_links_and_newlines_survive(self):
        self.assertEqual(self.codec.encode('「《A》」\n　'),
                         '「《'.encode('cp932')+struct.pack('>H',self.codec.codes['A'])+'》」\n　'.encode('cp932'))
        self.assertEqual(self.codec.encode('\n',newline='\r\n'),b'\r\n')

    def test_unsupported_glyph_cannot_silently_disappear(self):
        with self.assertRaises(UnicodeEncodeError):self.codec.encode('🙂')


class BinaryFormats(unittest.TestCase):
    def test_indexed_text_grows_without_losing_neighbor(self):
        class Encoder:
            def encode(self,s,**kw):return s.encode()
        obj=Build.__new__(Build);obj.codec=Encoder();obj.routes={}
        source='名前'.encode('cp932');pool=source+b'\0untouched\0'
        raw=bytearray(b'SB2T'+bytes(12)+b'DIXT'+bytes(12)+struct.pack('>II',0,len(source)+1)+b'TDXT'+bytes(12)+pool)
        struct.pack_into('>I',raw,24,8);struct.pack_into('>I',raw,48,len(pool))
        row={'id':'test','locator':'index:0','encoding':'cp932','jp':'名前','english':'A much longer translated label'}
        out=obj.indexed(bytes(raw),[row]);base=56
        a,b=struct.unpack_from('>II',out,32)
        self.assertEqual(out[base+a:out.index(0,base+a)],row['english'].encode())
        self.assertEqual(out[base+b:out.index(0,base+b)],b'untouched')
        self.assertEqual(struct.unpack_from('>I',out,48)[0],len(out)-base)

    def test_keyword_library_index_and_decode_extent_agree(self):
        path=ROOT/'work/pkg/USRDIR/COMMONDATA_REN/MTDATA/MTV_ALL_KEYWORD_DEF.CPK'
        if not path.exists():self.skipTest('Ignored source assets not present')
        from cpk import CPK
        import non_dialogue as nd
        class Encoder:
            # Tiny synthetic glyphs keep this test about binary index growth.
            codes={chr(c):0x8140 for c in range(32,127)}
            widths={0:1}
            def encode(self,s,**kw):return s.encode()
        obj=Build.__new__(Build);obj.codec=Encoder();obj.routes={}
        k=CPK(str(path));raw=k.read(k.files[0]);rows=[]
        for identity,tag,offset,jp in nd.mtfl_fields(raw):
            rows.append({'id':str(identity)+tag,'entry':identity,'locator':str(identity)+':'+tag,
                         'jp':jp,'english':'Long translation '+str(identity)+tag+' '+('x'*200)})
        out=obj.mtfl(raw,rows);marker=out.find(b'ENDoMTFLs');j=out.find(b'jstr')
        self.assertGreater(len(out),len(raw))
        self.assertEqual(struct.unpack_from('<I',out,j+12)[0],marker-j-16)
        self.assertEqual(struct.unpack_from('<I',out,0x2c)[0],marker-0x30)
        self.assertEqual(out[marker:],raw[raw.find(b'ENDoMTFLs'):])


if __name__=='__main__':unittest.main()
