"""Measured reward composition and native Rengoku sprite sampling."""
import unittest,sys,struct,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from build_game import Build
from rengoku_runtime import DEFAULT_FONT
from rengoku_search_layout import FSSA_ASSET,field
from rengoku_screenshot_layout import line_width
import rengoku_maximum_break_art as M
import rengoku_attack_art as A

class Category020(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.b=Build(DEFAULT_FONT)
 def test_rewards_have_one_message_and_one_preserved_amount(self):
  raw=self.b.asset(FSSA_ASSET);out=self.b.fssa(raw,self.b.byasset[FSSA_ASSET])
  for p in (0x8bfe4,0x99d84):self.assertEqual(field(out,p),b'')
  for p in (0x8bfc4,0x99d64):self.assertEqual(field(out,p),self.b.codec.encode('SR Point earned.'))
  self.assertEqual(field(out,0x99da4),self.b.codec.encode('Bonus funds received:'))
  self.assertEqual(field(out,0x99dc4),field(raw,0x99dc4))
  r=self.b.reward_report[-1];self.assertEqual(r['amount_x']-r['label_x']-r['label_width'],18)
  self.assertAlmostEqual((r['label_x']+r['amount_x']+r['amount_width'])/2,639.5)
  for p in (0x99da4,0x99dc4):self.assertEqual(out[p+8:p+23],raw[p+8:p+23]);self.assertFalse(out[p+23]&0x40)
 def test_all_keyword_links_have_word_spacing_and_story_still_fits(self):
  for path in (ROOT/'localization/locales/en').glob('STG*.json'):
   self.assertIsNone(re.search(r'》[A-Za-z]',path.read_text(encoding='utf8')),str(path))
  en=self.b.story['rengoku:STGZ3REN_00045:00052']
  self.assertIn('ZONE》 ran',en)
  self.assertLessEqual(max(line_width(self.b.codec,s,32) for s in en.split('\n')[1:]),870)
 def test_maximum_break_native_pieces_settle_contiguously_and_preserve_other_bytes(self):
  raw=self.b.asset('work/pkg/USRDIR/DATA_REN/BTLC/CMN.CPK:0');out=M.apply(raw,DEFAULT_FONT);M.verify(raw,out,DEFAULT_FONT)
  right=-736
  for p,ax,ay,_ in M.BANNER_PIECES:
   l,t,r,b,u,v,s,q=struct.unpack_from('>4h4H',out,p)
   self.assertEqual(l+ax,right);self.assertEqual((t+ay,b+ay),(-88,88));right=r+ax
   ink=M.texture(out,16).crop((u,v,s,q));box=ink.getchannel('A').getbbox()
   self.assertGreater(box[0],0);self.assertLess(box[2],ink.width)
  self.assertEqual(right,736)
  self.assertEqual(M.texture(raw,1).tobytes(),M.texture(out,1).tobytes())
  bad=bytearray(out);bad[0]^=1
  with self.assertRaises(AssertionError):M.verify(raw,bytes(bad),DEFAULT_FONT)
 def test_attack_tiles_use_actual_native_uvs_and_reject_drift(self):
  raw=self.b.asset('work/pkg/USRDIR/DATA_REN/AIDDATA/AIDDATAPACK_R.CPK:1');fssa=self.b.asset(FSSA_ASSET)
  out=A.apply(raw,raw,fssa);self.assertEqual(len(out),len(raw));self.assertNotEqual(out,raw)
  bad=bytearray(fssa);bad[0x4a408+12]^=1
  with self.assertRaises(ValueError):A.apply(raw,raw,bytes(bad))
if __name__=='__main__':unittest.main()
