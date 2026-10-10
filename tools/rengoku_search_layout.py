"""NPJB00689 search/ally-list labels and measured Effect-panel wrapping.

Only source-identified display records change. RPW mechanics and strings stay
intact; descriptions are supplied through the existing owned draw-hook pool.
"""
import struct

from rengoku_runtime import require, sha
from rengoku_screenshot_layout import line_width
from source_text import rpw_chunks, rpw_strings

RPW_ASSET = 'work/pkg/USRDIR/COMMONDATA_REN/MTDATA/RPW_DATA.CPK:0'
RPW_SHA = '843f9d59af70515da1087c67bcffca7b570eb4a0eae2cb70e31bf06665f30872'
FSSA_ASSET = 'work/pkg/USRDIR/DATA_REN/AIDDATA/AIDDATAPACK_R.CPK:0'
# At native 1280px, the supplied Effect screenshot has x=141.5 and a
# right rule near 1224. Its Rodin text uses a 28px quad: the visible prefix
# ending "Negates Daunt" measures 1142.75px and is clipped as observed.
# Reserve >80px inside that right edge. The native ruler explicitly says
# two lines for Spirits and up to three for skill/ability descriptions.
EFFECT_WIDTH = 1000
EFFECT_QUAD = 28

LABELS = {
    0x96f24: ('精神コマンド', 'Spirits'),
    0x96fa4: ('精神コマンド', 'Spirits'),
    0x97024: ('精神コマンド', 'Spirits'),
    0x970a4: ('精神', 'Spirits'),
    0x97104: ('精神コマンド', 'Spirits'),
    0x96f64: ('特殊能力', 'Abilities'),
    0x96fe4: ('特殊能力', 'Abilities'),
    0x97064: ('特殊能力', 'Abilities'),
    0x970e4: ('特殊能力', 'Abilities'),
    0x97144: ('特殊能力', 'Abilities'),
    # This is one heading stored in TWO records; keep the native SP value
    # column at 0x9d424. The suffix at 0x9d404 is only a decorative label.
    0x9d3e4: ('消費\n', 'SP Cost\n'),
    0x9d404: ('ＳＰ', ''),
    0x9ed84: ('気力', 'Foc'),
    0xa2684: ('気力', 'Foc'),
}
for _row in (0x9f344, 0x9f584, 0xa3ae4, 0xa3e04):
    LABELS[_row] = ('修理', 'Rpr.')
    LABELS[_row + 32] = ('補給', 'Res.')
for _row in (0x9f5c4, 0xa3b24):
    LABELS[_row] = ('援護攻撃', 'Sup Atk')
    LABELS[_row + 32] = ('援護防御', 'Sup Def')


def field(raw, row):
    base = struct.unpack_from('>I', raw, 0x20)[0]
    ptr = base + struct.unpack_from('>I', raw, row)[0]
    require(base <= ptr < len(raw), 'Search label pointer')
    return raw[ptr:raw.index(0, ptr)]


def apply_fssa(source, built, codec):
    out = bytearray(built)
    base = struct.unpack_from('>I', source, 0x20)[0]
    allowed, report = set(), []
    for row, (jp, en) in sorted(LABELS.items()):
        require(field(source, row) == jp.encode('cp932'), 'Search source label ' + hex(row))
        ptr = len(out)
        out.extend(codec.encode(en) + b'\0')
        struct.pack_into('>I', out, row, ptr - base)
        allowed.update(range(row, row + 4))
        width = line_width(codec, en.rstrip('\n'), source[row + 19])
        report.append({'row': hex(row), 'source': jp, 'display': en,
                       'width': width, 'style_and_position_preserved': True})
    require(all(a == b or i in allowed for i, (a, b) in enumerate(zip(built, out))),
            'Search changed non-pointer metadata')
    return bytes(out), report


def wrap_effect(codec, text, lines, width=EFFECT_WIDTH, quad=EFFECT_QUAD):
    # Reflow prose only: no loss of punctuation, mechanics or conditional
    # clauses. Original translation catalogs remain the full English source.
    result, current = [], ''
    for word in text.split():
        trial = current + ' ' + word if current else word
        if current and line_width(codec, trial, quad) > width:
            result.append(current)
            current = word
        else:
            current = trial
        require(line_width(codec, current, quad) <= width,
                'Effect word exceeds the panel: ' + word)
    if current:
        result.append(current)
    require(0 < len(result) <= lines, 'Effect needs more than %d lines: %s' % (lines, text))
    out = '\n'.join(result)
    require(out.split() == text.split(), 'Effect wrapping changed content')
    return out


def effect_hooks(raw, rows, codec):
    require(sha(raw) == RPW_SHA, 'Rengoku RPW source changed')
    strings = {s['body_offset']: s for s in rpw_strings(raw)}
    catalog = {r['offset']: r for r in rows}
    chunks = {c['name']: c for c in rpw_chunks(raw)}
    hooks, report = {}, []
    # Independently checked Rengoku arrays: 82 x 13 words and 44 x 5 words.
    # Columns 4/5 are long/short skill prose; Spirit column 3 is its effect.
    # Zero records and the last hidden Spirit entry have no prose to wrap.
    for family, stride, count, columns, max_lines in (
            ('sk-pri', 13, 82, (4, 5), 3), ('spirit', 5, 44, (3,), 2)):
        ch = chunks[family]
        require(ch['body_end'] - ch['body_offset'] == stride * count * 4,
                'Rengoku description table shape: ' + family)
        for record in range(1, count):
            start = ch['body_offset'] + record * stride * 4
            name = strings[struct.unpack_from('<I', raw, start + 4)[0]]['jp']
            for column in columns:
                offset = struct.unpack_from('<I', raw, start + column * 4)[0]
                require(offset in strings, 'Description pointer is not a string start')
                source = strings[offset]
                if source['jp'] in ('－', '－－', '？'):
                    require(family == 'spirit' and record == 43, 'Unexpected empty effect')
                    continue
                row = catalog.get(source['offset'])
                require(row and row['jp'] == source['jp'], 'Missing source-bound effect English')
                width,quad = (760,32) if family=='sk-pri' else (EFFECT_WIDTH,EFFECT_QUAD)
                display = wrap_effect(codec, row['english'], max_lines,width,quad)
                key, value = source['jp'].encode('cp932'), codec.encode(display)
                require(key not in hooks or hooks[key] == value, 'Conflicting shared effect')
                hooks[key] = value
                report.append({'family': family, 'record': record, 'column': column,
                               'name': name, 'occurrence': row['id'], 'display': display,
                               'width_limit':width, 'glyph_quad':quad,
                               'line_widths': [line_width(codec, s, quad)
                                               for s in display.split('\n')],
                               'max_lines': max_lines})
    return hooks, {'width_limit': EFFECT_WIDTH, 'glyph_quad': EFFECT_QUAD,
                   'bindings': len(report), 'unique_descriptions': len(hooks), 'rows': report}
