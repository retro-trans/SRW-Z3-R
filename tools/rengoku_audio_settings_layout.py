"""Source-bound audio/settings captions that respect native control columns.

All offsets belong to NPJB00689's own FSSA member. Only display pointers
change: sliders, button sprites, line pitch and option values stay native.
"""
import struct

from rengoku_runtime import require
from rengoku_search_layout import field
from rengoku_screenshot_layout import line_width

AUDIO_ROWS = (0x94504, 0x945a4, 0x94604, 0x946a4)
HEADER_ROWS = (0x93e24, 0x93f44, 0x94124)
CONFIRM_ROWS = (0x8c4a4, 0x8c504, 0x8c564, 0x8c704, 0x8c7e4, 0x8c8c4)
PLAY_ROWS = (0x94524, 0x945c4, 0x94624, 0x946c4)
MAP_ROW = 0x94d44
MAXIMUM_ROWS = (0x94564, 0x94664)


def plan(source, codec, english):
    """Return concrete replacements without mutating source or catalogs."""
    result = []

    def add(row, jp, text, limit, quad=None):
        require(field(source, row) == jp.encode('cp932'),
                'Audio/settings source changed: ' + hex(row))
        quad = quad or source[row + 19]
        widths = [line_width(codec, ln, quad) for ln in text.split('\n')]
        require(max(widths, default=0) <= limit,
                'Audio/settings caption exceeds its control column: ' + hex(row))
        result.append(dict(row=hex(row), source=jp, display=text,
                           quad=quad, line_widths=widths, width_limit=limit))

    for row in AUDIO_ROWS:
        jp = field(source, row).decode('cp932')
        require(jp.startswith('・音声設定（　：　　）\n・ＳＥ設定\n・ＢＧＭ設定'),
                'Audio composite source changed')
        require(source[row + 16:row + 24].hex() == '1c1c1a1c1c280100',
                'Audio composite layout changed')
        text = english[jp]
        lines = text.split('\n')
        require(lines[0] == '・Voice Settings (　:　　)', 'Voice translation baseline changed')
        # The triangle is a separate sprite and Play a separate FSSA draw.
        # Remove the old inline punctuation and put ": Play" in that draw.
        lines[0] = '・Voice'
        lines = [ln.replace('・Remember Sort / Sub Information',
                            '・Remember Sort / Info') for ln in lines]
        require(len(lines) == len(jp.split('\n')), 'Audio row pitch changed')
        add(row, jp, '\n'.join(lines), 380)
        require(line_width(codec, lines[0], 28) < 160,
                'Voice label touches native triangle')
    for row in PLAY_ROWS:
        add(row, '再生', ': Play', 105)
    jp = field(source, MAP_ROW).decode('cp932')
    require(jp.endswith('・ソート・サブ情報の記憶'), 'Map settings composite changed')
    text = english[jp].replace('・Remember Sort / Sub Information', '・Remember Sort / Info')
    # Quick Commands includes native inline button slots across the row.
    # Its full line is wider than the left label column by design; the
    # remembered-sort label still must end before the ON/OFF bracket.
    require(line_width(codec, text.split('\n')[-1], 28) <= 380,
            'Map remembered-sort label touches value bracket')
    add(MAP_ROW, jp, text, 600)
    for row in MAXIMUM_ROWS:
        add(row, '・マキシマムブレイク', '・Max. Break', 230)
    for first in HEADER_ROWS:
        # One heading is split across four physical records. Join it once,
        # retaining the separate Target/Replace subheading and button icons.
        add(first, '【Ｂ', 'BGM Setup', 180)
        for delta, jp in ((32, '設定'), (64, 'ＧＭ'), (96, '】'), (128, '：')):
            add(first + delta, jp, '', 0)
        jp = '選曲対象' if first == HEADER_ROWS[0] else '置き換え'
        add(first + 160, jp, 'Target' if first == HEADER_ROWS[0] else 'Replace', 125)
        require(24.5 + line_width(codec, 'BGM Setup', 31) + 20 < 223.5,
                'BGM heading touches subheading')
    # These native Confirm-to-Play gaps are 88/112/128px, including the
    # intervening 32px button sprite. "Confirm" cannot fit the narrowest.
    # Apply the same short action to all six BGM control variants.
    for row in CONFIRM_ROWS:
        require(source[row + 19] == 21 and source[row + 22] & 15 == 6,
                'BGM control font preset changed')
        add(row, '：決定', ': OK', 48, quad=21)
    add(0x8c424, '：変更', ': Chg.', 88, quad=21)
    return result


def apply_fssa(source, built, codec, english):
    rows = plan(source, codec, english)
    out = bytearray(built)
    base = struct.unpack_from('>I', source, 0x20)[0]
    for item in rows:
        row = int(item['row'], 16)
        dest = len(out)
        out.extend(codec.encode(item['display']) + b'\0')
        struct.pack_into('>I', out, row, dest - base)
    allowed = {p for item in rows for p in range(int(item['row'], 16), int(item['row'], 16) + 4)}
    require(all(a == b or p in allowed for p, (a, b) in enumerate(zip(built, out))),
            'Unlisted audio/settings metadata change')
    for item in rows:
        require(field(out, int(item['row'], 16)) == codec.encode(item['display']),
                'Audio/settings relocation readback failed')
    return bytes(out), rows
