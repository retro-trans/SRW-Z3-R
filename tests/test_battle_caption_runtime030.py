"""Execute native conversion and the compiled draw lookup beside portrait state."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from build_game import Build
import rengoku_runtime as R
import rengoku_battle_subtitles as L
import rengoku_battle_caption_runtime as C
from rengoku_screenshot_layout import line_width
from test_link_runtime import CPU

REPORTED=('battle:49f842858cf2eb48','battle:5e66fdb7e4d3fa5b','battle:0b0a817d31a85d06')

def converter(cpu):
    cpu.r[2]=0x953f88
    cpu.calls[0x67db24]=lambda c:(c.r[3]+c.string(c.r[3]).find(c.string(c.r[4]))
        if c.string(c.r[4]) in c.string(c.r[3]) else 0)
    def copy_n(c):c.put(c.r[3],c.read(c.r[4],c.r[5]));return c.r[3]
    def copy_z(c):c.put(c.r[3],c.string(c.r[4])+b'\0');return c.r[3]
    cpu.calls[0x6832c0]=copy_n;cpu.calls[0x682eac]=copy_z

class CaptionRuntime030(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT/'work/pkg').exists():raise unittest.SkipTest('Private assets unavailable')
        cls.b=Build(R.DEFAULT_FONT)
        cls.rows={r['message']:r for r in cls.b.bocc.values() if isinstance(r.get('bank'),int)}

    def test_reported_english_overwrites_state_before_fix(self):
        for key in REPORTED:
            row=self.rows[key];c=CPU(self.b.original_elf);converter(c)
            obj,src=0x2200000,0x2210000;dest=obj+0xfb3
            c.put(obj,b'\x55'*0x1100);c.put(src,self.b.codec.encode(row['english'])+b'\0')
            c.r[3],c.r[4]=dest,src;c.run(0x12c3b4,{0x10000})
            self.assertGreater(len(c.string(dest))+1,C.NATIVE_CAPACITY)
            self.assertNotEqual(c.read(obj+0x1039,8),b'\x55'*8,key)

    def test_native_buffers_preserve_portrait_state_and_draw_complete_owned_english(self):
        for key in REPORTED:
            row=self.rows[key];c=CPU(self.b.elf);converter(c)
            obj,src=0x2200000,0x2210000;dest=obj+0xfb3
            c.put(obj,b'\x55'*0x1100);c.put(src,row['jp'].encode('cp932')+b'\0')
            c.r[3],c.r[4]=dest,src;c.run(0x12c3b4,{0x10000})
            native=row['jp'].replace('\\n','\n').encode('cp932')
            self.assertEqual(c.string(dest),native)
            self.assertEqual(c.read(obj+0x1039,8),b'\x55'*8)
            # The real draw entry resolves the complete converted Japanese
            # key to English outside the object, after all bounded copies.
            c.r[3],c.r[7],c.lr=dest,1,0x10000
            c.run(R.DRAW,{R.DRAW+4})
            display,reason=L.fit(self.b.codec,row['english'])
            self.assertIsNone(reason)
            self.assertEqual(c.string(c.r[3]),self.b.codec.encode(display.replace('\\n','\n')))
            self.assertGreaterEqual(c.r[3],R.TEXT)
            self.assertEqual(c.read(obj+0x1039,8),b'\x55'*8)
            self.assertTrue(all(line_width(self.b.codec,s,32)<=730 for s in display.split('\\n')))

    def test_all_native_captions_and_cues_keep_capacity_and_binding(self):
        self.assertEqual(self.b.srvc,(ROOT/'work/pkg/USRDIR/DATA_REN/BTLC/SRVC.BIN').read_bytes())
        self.assertEqual(self.b.caption_runtime_report['native_source_occurrences'],5077)
        self.assertGreaterEqual(self.b.caption_runtime_report['previous_unsafe_english_occurrences'],len(REPORTED))
        self.assertEqual(self.b.subtitle_report['pending'],[])
        self.assertLessEqual(self.b.caption_runtime_report['native_source_max_bytes'],134)
        for row in self.rows.values():
            key=row['jp'].replace('\\n','\n').encode('cp932')
            self.assertLessEqual(len(key)+1,134)
            self.assertIn(key,self.b.hooks)
        bad=bytearray(self.b.original_elf);bad[0x12c0a0-0x10000]^=1
        with self.assertRaises(ValueError):C.guard(bad)

    def test_honorifics_before_permission_and_story_bounds(self):
        for suffix in ('00015','00025','00036'):
            text=self.b.story['rengoku:STGZ3REN_00015:'+suffix]
            self.assertIn('Mr. Blue',text)
            if suffix=='00015':self.assertIn('Mr. Advent',text)
            self.assertTrue(all(line_width(self.b.codec,s,32)<=870 for s in text.split('\n')[1:]))
        self.assertNotIn('Mr. Advent',self.b.story['rengoku:STGZ3REN_00015:00040'])

if __name__=='__main__':unittest.main()
