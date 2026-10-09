"""Rengoku team-list support columns, Move footer and settings tab states."""
import struct

from rengoku_runtime import require
from rengoku_search_layout import field
from rengoku_screenshot_layout import line_width

TABS = {row: ('システム設定' + ('１' if i % 2 == 0 else '２'),
              'Settings ' + str(1 + i % 2))
        for i, row in enumerate(range(0x96e24, 0x96f24, 32))}
SUPPORT = {
    0x9f884: ('援攻', 'S. Atk'), 0x9f8a4: ('援防', 'S. Def'),
    0xa35e4: ('援攻', 'S. Atk'), 0xa3604: ('援防', 'S. Def'),
    0xa4584: ('援攻', 'S. Atk'), 0xa45a4: ('援防', 'S. Def'),
}
FOOTER = {0xa29a4: '【】', 0xa29c4: '空陸－地', 0xa29e4: '９９／'}
MOVE = (0x9eea4, 0xa2984)


def x(raw, row):
    return 640 + struct.unpack_from('>f', raw, row + 4)[0] * 640


def apply_fssa(source, built, codec):
    out = bytearray(built)
    base = struct.unpack_from('>I', source, 0x20)[0]
    allowed, report = set(), []
    for row, (jp, en) in sorted({**TABS, **SUPPORT}.items()):
        require(field(source, row) == jp.encode('cp932'), 'Roster/settings label ' + hex(row))
        ptr = len(out)
        out.extend(codec.encode(en) + b'\0')
        struct.pack_into('>I', out, row, ptr - base)
        allowed.update(range(row, row + 4))
        if row in SUPPORT:
            # These are two-cell Japanese headings, with only 72px between
            # the first two variants. Use the same 21px S. Atk/S. Def recipe
            # as Z3.1; center on this game's original two-cell header span.
            require(source[row + 18:row + 24] == bytes((26, 28, 28, 28, 49, 0)),
                    'Team support style ' + hex(row))
            width = line_width(codec, en, 21)
            require(width <= 63, 'Team support label exceeds narrow column')
            new_x = x(source, row) + (56 - width) / 2
            struct.pack_into('>f', out, row + 4, (new_x - 640) / 640)
            out[row + 16:row + 22] = bytes((21, 21, 19, 21, 21, 21))
            allowed.update(range(row + 4, row + 8))
            allowed.update(range(row + 16, row + 22))
            report.append({'row': hex(row), 'source': jp, 'display': en,
                           'width': width, 'glyph_quad': 21,
                           'old_x': x(source, row), 'new_x': new_x})
        else:
            require(source[row + 16:row + 24] == bytes((255, 255, 27, 31, 28, 31, 0, 64)),
                    'Settings tab style ' + hex(row))
            width = line_width(codec, en, 31)
            require(width < 210, 'Settings tab exceeds its button')
            report.append({'row': hex(row), 'source': jp, 'display': en,
                           'width': width, 'style_and_position_preserved': True})
    # Rengoku's footer is composed from three separate records. Translate
    # only through the existing paths; shift bracket, value and terrain
    # together, retaining their own internal spacing and original glyphs.
    for row, jp in FOOTER.items():
        require(field(source, row) == jp.encode('cp932'), 'Team footer source ' + hex(row))
        new_x = x(source, row) + 32
        struct.pack_into('>f', out, row + 4, (new_x - 640) / 640)
        allowed.update(range(row + 4, row + 8))
        report.append({'row': hex(row), 'source': jp, 'old_x': x(source, row),
                       'new_x': new_x, 'translation_and_style_preserved': True})
    for row in MOVE:
        require(field(source, row) == '移動'.encode('cp932'), 'Move footer label source')
        require(source[row + 19] == 24, 'Move footer font size')
        require(x(out, 0xa29a4) - x(out, row) - line_width(codec, 'Move', 24) >= 9.9,
                'Move footer label touches value bracket')
    require(source[0xa29a4 + 20] == 176 and source[0xa29a4 + 19] == 25,
            'Footer bracket internal span changed')
    require(x(out, 0xa29a4) + 176 + 25 < 640, 'Footer exceeds its strip')
    require(all(a == b or i in allowed for i, (a, b) in enumerate(zip(built, out))),
            'Unlisted roster/settings edit')
    return bytes(out), report
