"""Battle-bank bounds and literal subtitle control sequences."""
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from battle_lines import parse_blocks,discover_table,check_target


class BattleBankTests(unittest.TestCase):
    def bank(self):
        raw=bytearray(48);raw[0]=3
        struct.pack_into('<H',raw,6,2)
        text='「甲」'.encode('cp932');raw[32:32+len(text)]=text
        return raw

    def test_shared_string_retains_both_index_entries(self):
        block=parse_blocks(self.bank(),[0,48])[0]
        self.assertEqual(block['pool'],32)
        self.assertEqual(block['strings'],[{'offset':32,'jp':'「甲」','index_entries':[0,1]}])

    def test_pointer_must_stay_in_its_bank(self):
        raw=self.bank();struct.pack_into('<I',raw,24,16)
        with self.assertRaises(ValueError):parse_blocks(raw,[0,48])

    def test_pointer_cannot_start_inside_multibyte_text(self):
        raw=self.bank();struct.pack_into('<I',raw,24,1)
        with self.assertRaises(ValueError):parse_blocks(raw,[0,48])

    def test_header_counts_cannot_consume_the_next_bank(self):
        raw=self.bank();raw[1]=255
        with self.assertRaises(ValueError):parse_blocks(raw,[0,48])

    def test_discovery_uses_local_data_not_fixed_sibling_addresses(self):
        raw=bytearray(32);raw[0]=raw[16]=3
        table=b'\xff'*8+struct.pack('>III',0,16,32)+b'\xff'*8
        start,offsets,blocks=discover_table(raw,table)
        self.assertEqual((start,offsets,len(blocks)),(8,[0,16,32],2))
        with self.assertRaises(ValueError):discover_table(raw,table+table)

    def test_literal_line_break_must_not_become_a_host_newline(self):
        check_target('「攻撃\\n開始！」','「Attack\\nnow!」',[])
        with self.assertRaises(ValueError):check_target('「攻撃\\n開始！」','「Attack\nnow!」',[])

    def test_speech_wrappers_cannot_be_dropped(self):
        with self.assertRaises(ValueError):check_target('「攻撃！」','Attack!',[])

    def test_retreat_quote_actual_newline_is_preserved(self):
        check_target('「撤退\n開始！」','「Begin\nretreat!」',[])
        with self.assertRaises(ValueError):check_target('「撤退\n開始！」','「Begin retreat!」',[])


if __name__=='__main__':unittest.main()
