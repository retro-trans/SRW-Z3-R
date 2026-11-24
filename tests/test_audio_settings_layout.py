"""Actual NPJB00689 settings columns and split BGM caption regressions."""
from pathlib import Path
import struct,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_game import Build
from rengoku_runtime import DEFAULT_FONT
from rengoku_search_layout import FSSA_ASSET,field
from rengoku_screenshot_layout import line_width
import rengoku_audio_settings_layout as L

class AudioSettings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT/'work/pkg').exists():raise unittest.SkipTest('Private source assets unavailable')
        cls.b=Build(DEFAULT_FONT);cls.raw=cls.b.asset(FSSA_ASSET)
        cls.en={r['jp']:r['english'] for r in cls.b.byasset[FSSA_ASSET]}
        cls.out=cls.b.fssa(cls.raw,cls.b.byasset[FSSA_ASSET])

    def test_all_audio_states_clear_voice_button_and_value_bracket(self):
        for p in L.AUDIO_ROWS:
            jp=field(self.raw,p).decode('cp932');old=self.en[jp].split('\n')
            self.assertGreater(line_width(self.b.codec,old[0],28),200)
            item=next(r for r in self.b.audio_settings_report if int(r['row'],16)==p)
            text=item['display'];lines=text.split('\n')
            self.assertEqual(len(lines),len(jp.split('\n')))
            self.assertEqual(lines[0],'・Voice')
            self.assertLess(191.5+line_width(self.b.codec,lines[0],28),350)
            for line in lines:self.assertLess(191.5+line_width(self.b.codec,line,28),599.5-20)
            if 'Remember Sort' in text:
                self.assertIn('・Remember Sort / Info',text)
                self.assertGreater(191.5+line_width(self.b.codec,old[-1],28),599.5)
            self.assertEqual(field(self.out,p),self.b.codec.encode(text))
        for p in L.PLAY_ROWS:
            self.assertEqual(field(self.out,p),self.b.codec.encode(': Play'))
            self.assertLess(413.5+line_width(self.b.codec,': Play',28),520)

    def test_split_bgm_headers_do_not_touch_subheading_or_first_button(self):
        for p in L.HEADER_ROWS:
            self.assertEqual(field(self.out,p),self.b.codec.encode('BGM Setup'))
            for delta in (32,64,96,128):self.assertEqual(field(self.out,p+delta),b'')
            self.assertLess(24.5+line_width(self.b.codec,'BGM Setup',31)+20,223.5)
            text='Target' if p==L.HEADER_ROWS[0] else 'Replace'
            self.assertEqual(field(self.out,p+160),self.b.codec.encode(text))
            self.assertLess(223.5+line_width(self.b.codec,text,24)+20,350)

    def test_control_captions_fit_smallest_native_icon_gap(self):
        # Source BGM selector has just 88px between label anchors; the
        # next 32px icon and an 8px reserve leave 48px for the first action.
        self.assertGreater(line_width(self.b.codec,': Confirm',21),48)
        for p in L.CONFIRM_ROWS:
            self.assertEqual(field(self.out,p),self.b.codec.encode(': OK'))
            self.assertLessEqual(line_width(self.b.codec,': OK',21),48)
        self.assertEqual(field(self.out,0x8c424),self.b.codec.encode(': Chg.'))
        self.assertLessEqual(line_width(self.b.codec,': Chg.',21),88)

    def test_original_geometry_values_and_icons_are_unchanged(self):
        out,report=L.apply_fssa(self.raw,self.raw,self.b.codec,self.en)
        self.assertEqual(len(report),36)
        allowed={q for r in report for q in range(int(r['row'],16),int(r['row'],16)+4)}
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(self.raw,out))))
        for r in report:
            p=int(r['row'],16)
            self.assertEqual(out[p+4:p+32],self.raw[p+4:p+32])
        # All native option brackets and values remain byte-for-byte intact.
        for p in (0x94544,0x945e4,0x94644,0x946e4,0x94704,0x94724,0x94d64):
            self.assertEqual(out[p:p+32],self.raw[p:p+32])

    def test_source_style_and_translation_drift_are_rejected(self):
        bad=bytearray(self.raw);bad[L.AUDIO_ROWS[0]+19]=27
        with self.assertRaises(ValueError):L.plan(bad,self.b.codec,self.en)
        bad=bytearray(self.raw);bad[L.CONFIRM_ROWS[0]+22]=0
        with self.assertRaises(ValueError):L.plan(bad,self.b.codec,self.en)
        en=dict(self.en);en[field(self.raw,L.AUDIO_ROWS[0]).decode('cp932')]='Changed baseline'
        with self.assertRaises(ValueError):L.plan(self.raw,self.b.codec,en)

if __name__=='__main__':unittest.main()
