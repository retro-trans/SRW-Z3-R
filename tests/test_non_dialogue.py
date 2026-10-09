"""Reject malformed text spans and translation damage without game fixtures."""
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from non_dialogue import credit_fields, map_fields, recap_fields, scan_nul, validate_target, occurrence_text
from inspect_artwork import texture_blocks


class TranslationGuards(unittest.TestCase):
    def test_printf_order_and_width_survive(self):
        validate_target('資金%08d／%s', 'Funds %08d / %s', [])
        for target in ('Funds %d / %s', 'Funds %s / %08d', 'Funds %08d'):
            with self.subTest(target=target), self.assertRaises(ValueError):
                validate_target('資金%08d／%s', target, [])

    def test_percent_in_prose_is_not_a_printf_token(self):
        validate_target('５０％', '50% per turn', [])

    def test_runtime_keys_and_controls_cannot_be_dropped(self):
        source='【必要容量】\x01$n'
        validate_target(source, source, [])
        for target in ('【必要容量】$n', 'Required space\x01$n', '【必要容量】\x01'):
            with self.subTest(target=target), self.assertRaises(ValueError):
                validate_target(source, target, [])

    def test_untranslated_prose_and_private_glyphs_fail(self):
        for text in ('Attack 攻撃', 'Attack\ue000'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                validate_target('攻撃', text, [])

    def test_contextual_override_does_not_change_other_occurrences(self):
        entry={'text':'Defend', 'occurrences':['command','stat'],
               'occurrence_overrides':{'stat':{'text':'Defense'}}}
        self.assertEqual(occurrence_text(entry,'stat'),'Defense')
        self.assertEqual(occurrence_text(entry,'command'),'Defend')
        with self.assertRaises(ValueError):
            occurrence_text(entry,'foreign')


class DiscoveryBounds(unittest.TestCase):
    def test_ideographic_spaces_do_not_hide_strings(self):
        raw=b'\0'+ '第１話\u3000翠の地球'.encode('cp932') + b'\0'
        self.assertEqual(list(scan_nul(raw)),[(1,'cp932','第１話\u3000翠の地球')])

    def test_credit_fields_separate_binary_record_metadata(self):
        raw=bytearray(20+94)
        struct.pack_into('>H',raw,0,1)
        raw[20:24]='担当'.encode('cp932')
        raw[84:114]=b'\xff'*30
        self.assertEqual(list(credit_fields(raw)),[(20,'担当')])
        raw[26]=1
        with self.assertRaises(ValueError):
            list(credit_fields(raw))

    def test_credit_extent_cannot_escape_record_table(self):
        raw=bytearray(20)
        struct.pack_into('>H',raw,0,2)
        with self.assertRaises(ValueError):
            list(credit_fields(raw))

    def test_recap_may_fill_the_whole_bounded_span(self):
        raw=b'1001'+b'\0'*8+b'\xff'*4+'概要'.encode('cp932')
        self.assertEqual(list(recap_fields(raw)),[('1001',16,'概要')])

    def test_recap_pointer_cannot_go_out_of_bounds(self):
        raw=bytearray(b'1001'+b'\0'*8+b'\xff'*4+'概要'.encode('cp932'))
        struct.pack_into('>I',raw,8,1000)
        with self.assertRaises(ValueError):
            list(recap_fields(raw))

    def test_map_name_padding_and_extent_are_guarded(self):
        raw=bytearray(64)
        struct.pack_into('<I',raw,8,1)
        struct.pack_into('<II',raw,20,32,32)
        raw[36:40]='平地'.encode('cp932')
        self.assertEqual(list(map_fields(raw)),[(36,'平地')])
        bad=bytearray(raw); bad[63]=1
        with self.assertRaises(ValueError):
            list(map_fields(bad))
        struct.pack_into('<I',raw,8,2)
        with self.assertRaises(ValueError):
            list(map_fields(raw))

    def test_concatenated_texture_blocks_do_not_overlap(self):
        block=bytearray(52)
        block[:3]=b'\x02\x02\x00'
        struct.pack_into('>I',block,8,1)
        struct.pack_into('>III',block,12,0,48,4)
        self.assertEqual([off for off,_ in texture_blocks(b'HEAD'+block+block)],[4,56])
        struct.pack_into('>I',block,20,999)
        self.assertEqual(list(texture_blocks(block)),[])


if __name__=='__main__':
    unittest.main()
