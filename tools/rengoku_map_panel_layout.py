"""Map-hover labels, fixed-cell Spirit indicators and confirmation overlays."""
import struct

from rengoku_runtime import require, SPIRIT_LABELS, CHOICE_PAD
from rengoku_search_layout import field
from rengoku_screenshot_layout import line_width

FLAGS = dict(zip('熱魂闘閃不鉄集必加覚手狙突直幸努乱分', SPIRIT_LABELS))
STRIPS = {0xa7044: '熱魂闘閃不鉄集必加覚手狙突直幸努乱',
          0xa7064: '熱魂闘閃不鉄集必加覚手狙突直幸努乱',
          0xa7084: '熱魂闘閃不鉄集必加覚手狙突直／乱分',
          0xa70a4: '熱魂闘閃不鉄集必加覚手狙突直幸努乱',
          0xa70c4: '熱魂闘閃不鉄集必加覚手狙突直／乱分'}
SUPPORT = {0xa4dc4: ('援攻．\n援防．', 'Atk.\nDef.'),
           0xa6464: ('援攻．', 'Atk.'), 0xa6484: ('援攻．', 'Atk.'),
           0xa64c4: ('援防．', 'Def.'), 0xa64e4: ('援防．', 'Def.')}
MOVE = (0x9ac64, 0x9ace4, 0x9ad64)
FOCUS = (0x9a7a4, 0x9a864, 0x9a924, 0x9a9e4, 0x9aac4,
         0x9aca4, 0x9ad24, 0x9ada4)
RECOVERY = 0x9a4e4
CHOICES = ((0x8bd24, 0x8bd44, 'Yes'), (0x98f84, 0x98fa4, 'Yes'),
           (0x99364, 0x99384, 'Yes'), (0x993a4, 0x993c4, 'No'),
           (0x993e4, 0x99404, 'Yes'), (0x99424, 0x99444, 'No'))
CHOICE_SOURCE = 'はい　／　いいえ'
CHOICE_TEXT = 'Yes' + CHOICE_PAD + '／　No'


def status_text(jp):
    return ''.join(FLAGS.get(c, c) for c in jp)


def hooks(codec):
    return {jp.encode('cp932'): codec.encode(status_text(jp)) for jp in set(STRIPS.values())}


def apply_fssa(source, built, codec):
    out = bytearray(built)
    base = struct.unpack_from('>I', source, 0x20)[0]
    allowed, report = set(), []

    def replace(row, jp, en, size=None, budget=None):
        require(field(source, row) == jp.encode('cp932'), 'Map panel source ' + hex(row))
        ptr = len(out); out.extend(codec.encode(en) + b'\0')
        struct.pack_into('>I', out, row, ptr - base)
        allowed.update(range(row, row + 4))
        if size is not None:
            out[row + 16:row + 21] = bytes((size, size, size - 2, size, size))
            allowed.update(range(row + 16, row + 21))
        require(jp.count('\n') == en.count('\n'), 'Map panel line count changed')
        widths = [line_width(codec, s, size or source[row + 19]) for s in en.split('\n')]
        if budget is not None:
            require(max(widths) <= budget, 'Map panel label exceeds slot ' + hex(row))
        report.append({'row': hex(row), 'source': jp, 'display': en,
                       'widths': widths, 'quad': size or source[row + 19]})

    for row, jp in STRIPS.items():
        en = status_text(jp)
        require(len(codec.encode(en)) == len(jp.encode('cp932')), 'Spirit slot count changed')
        replace(row, jp, en)
        # Width 32 is the renderer's sentinel for the original cell pitch,
        # which may differ from the glyph quad in these narrow strips.
        report[-1]['slot_advance'] = source[row + 20]
        report[-1]['widths'] = [len(jp) * source[row + 20]]
    for row, (jp, en) in SUPPORT.items():
        replace(row, jp, en, 18, 50)
    for row in MOVE:
        replace(row, '移動', 'MV', 22, 36)
    for row in FOCUS:
        replace(row, '気力', 'Foc', budget=42)
    replace(RECOVERY, '回復：\n回復：', 'Rec:\nRec:', budget=54)
    # Keep original Yes/slash/No columns and cursor spans. The blank cell
    # tabs to three native pitches in the live advance adapter. Row bytes
    # 16..21 are pitches, NOT glyph quad dimensions: preset 1 uses 28px
    # quads here with 25px pitch. Both overlays use the same left alignment.
    for bg, active, word in CHOICES:
        require(source[bg + 16:bg + 22] == bytes.fromhex('191917191919'), 'Confirmation row metrics')
        require(source[active + 16:active + 22] == source[bg + 16:bg + 22], 'Confirmation overlay metrics')
        require(source[bg + 23] & 0xc0 == 0, 'Confirmation row alignment')
        require(source[bg + 22] & 0x0f == source[active + 22] & 0x0f == 1,
                'Confirmation font preset')
        replace(bg, CHOICE_SOURCE, CHOICE_TEXT)
        report[-1].update(quad=28, widths=None, native_pitch=25,
                          alignment_tab={'slash_column': 3, 'no_column': 5})
        require(field(source, active) == ('はい' if word == 'Yes' else 'いいえ').encode('cp932'), 'Confirmation overlay source')
        require(field(out, active) == codec.encode(word), 'Confirmation overlay translation')
        column = 0 if word == 'Yes' else 125
        xpos = struct.unpack_from('>f', source, bg + 4)[0] + column / 640
        struct.pack_into('>f', out, active + 4, xpos)
        out[active + 23] &= ~0x40
        allowed.update(range(active + 4, active + 8)); allowed.add(active + 23)
        report.append({'row': hex(active), 'display': word, 'background': hex(bg),
                       'column': column, 'alignment': 'left'})
    require(all(a == b or p in allowed for p, (a, b) in enumerate(zip(built, out))),
            'Unlisted map/confirmation edit')
    return bytes(out), report
