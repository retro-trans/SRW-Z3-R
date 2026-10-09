"""Source-bound Intermission, Pilot List and Pilot Training presentation fixes."""
import struct
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from rengoku_runtime import require, sha, DEFAULT_FONT
from rengoku_search_layout import field
from rengoku_screenshot_layout import line_width
from rengoku_roster_settings_layout import x

AID = 'USRDIR/DATA_REN/AIDDATA/AIDDATAPACK_R.CPK'
ART_SHA = 'db7ef062281e0f8f5ce7b72eb7d56db8ae2948ad673d8d4b9d61931c9c64a6a6'
HEADER_RECT = (0, 192, 296, 40)

LABELS = {
    # Shared dynamic stat captions and both roster/footer variants.
    **{r: ('格闘', 'MEL') for r in (0x8ed44, 0x8ed84, 0x8ee44, 0x8eea4,
                                      0x9f084, 0xa2c24, 0xa2e24, 0xa3fc4)},
    **{r: ('防御', 'DEF') for r in (0x9e184, 0x9ec24, 0x9ece4, 0x9f0e4,
                                      0xa2c84, 0xa2e84, 0xa4024)},
    0x9e304: ('所持\n必要\n残り', 'PP Held\nPP Cost\nPP Left'),
    0x9e324: ('ＰＰ\nＰＰ\nＰＰ', ''),
    # Names already appear before the live deployment totals.
    0x9b1e4: ('隊\n隻\n', ''), 0x9b3c4: ('隊\n隻\n', ''),
    # The large first-place counter shares this suffix with Pilot Info.
    # Bare totals on both screens avoid overflowing the next menu button.
    0x8f044: ('機', ''), 0x9b404: ('機', ''), 0x9b424: ('機', ''),
    # Leave room for the native NEW badge on Power Parts.
    0x9b604: ('強化パーツ', 'Parts'), 0x9b624: ('強化パーツ', 'Parts'),
}

# Four selected/inactive/transition variants. Join each physical pair.
CENTERS = {}
MENU_STYLES = {0x9b844: 0x9b484, 0x9b8a4: 0x9b4a4,
               0x9b904: 0x9b484, 0x9b964: 0x9b4a4}
FOOTER_STATS = (0x9ec04, 0x9ec24, 0x9ec44, 0x9ec64,
                0x9ecc4, 0x9ece4, 0x9ed04, 0x9ed24,
                *range(0xa2c24, 0xa2ce4, 32), *range(0xa2e24, 0xa2ee4, 32))
for first in range(0x96c24, 0x96e24, 128):
    LABELS[first] = ('パラメータ', 'Raise Stats')
    LABELS[first + 32] = ('上昇', '')
    LABELS[first + 64] = ('スキル', 'Learn Skills')
    LABELS[first + 96] = ('修得', '')
    CENTERS[first] = 727.5
    CENTERS[first + 64] = 995.5

# These menu words are assembled in three draws, not one centered string.
for first in (0x9b844, 0x9b8a4):
    LABELS[first] = ('チー', 'Team Setup')
    LABELS[first + 32] = ('編成', '')
    LABELS[first + 64] = ('ム', '')
for first in (0x9b904, 0x9b964):
    LABELS[first] = ('Ｄ', 'D-Trader')
    LABELS[first + 32] = ('ト', '')
    LABELS[first + 64] = ('レーダー', '')
for first in (0x9b0c4, 0x9b2a4):
    LABELS[first] = ('ＳＲ', 'SR Points')
    LABELS[first + 32] = ('ポイ', '')
    LABELS[first + 64] = ('ント．', '')
for first in (0x9b144, 0x9b324):
    LABELS[first] = ('Ｚ', 'Z Chips')
    LABELS[first + 32] = ('チップ．', '')


def apply_fssa(source, built, codec):
    # This game's Intermission sprite: one center + four XY/color/UV vertices,
    # a 304x40 native quad with 8px shear, sampling only the 296x40 word cell.
    uv = ((148/512, 212/512), (0, 192/512), (296/512, 192/512),
          (296/512, 232/512), (0, 232/512))
    for index, expected in enumerate(uv):
        require(struct.unpack_from('>2f', source, 0x4b95c + index * 20 + 12) == expected,
                'Rengoku Intermission heading UV changed')
    out = bytearray(built)
    base = struct.unpack_from('>I', source, 32)[0]
    allowed, report = set(), []
    for row, (jp, en) in sorted(LABELS.items()):
        require(field(source, row) == jp.encode('cp932'),
                'Intermission source changed: ' + hex(row))
        ptr = len(out)
        out.extend(codec.encode(en) + b'\0')
        struct.pack_into('>I', out, row, ptr - base)
        allowed.update(range(row, row + 4))
        if row in MENU_STYLES:
            template = MENU_STYLES[row]
            require(field(source, template) == 'パイロット一覧'.encode('cp932'),
                    'Complete menu-caption template changed')
            out[row + 4:row + 12] = source[template + 4:template + 12]
            out[row + 16:row + 24] = source[template + 16:template + 24]
            allowed.update(range(row + 4, row + 12))
            allowed.update(range(row + 16, row + 24))
        quad = out[row + 19]
        width = max((line_width(codec, ln, quad) for ln in en.split('\n')), default=0)
        if row in CENTERS:
            require(source[row + 16:row + 24] == bytes.fromhex('ffff1b1f1c1f0000'),
                    'Training tab style changed')
            require(width < 220, 'Training title exceeds tab')
            struct.pack_into('>f', out, row + 4, (CENTERS[row] - width / 2 - 640) / 640)
            allowed.update(range(row + 4, row + 8))
        if en in ('MEL', 'DEF'):
            require(width < quad * 2.5, 'Stat caption exceeds available column')
        if row == 0x9e304:
            require(width < 155 and source[row + 21] == 64,
                    'PP labels exceed original value column')
        report.append({'row': hex(row), 'source': jp, 'display': en,
                       'glyph_width': quad, 'width': width,
                       'x': x(out, row), 'original_x': x(source, row)})
    for row in FOOTER_STATS:
        require(field(source, row).decode('cp932') in ('格闘','射撃','技量','防御','回避','命中'),
                'Roster footer source changed')
        struct.pack_into('>f', out, row + 4, (x(source, row) - 10 - 640) / 640)
        allowed.update(range(row + 4, row + 8))
        report.append({'row': hex(row), 'footer_label_shift': -10,
                       'value_position_and_style_preserved': True})
    require(all(a == b or i in allowed for i, (a, b) in enumerate(zip(built, out))),
            'Unlisted Intermission edit')
    return bytes(out), report


def morton(xv, yv):
    return sum(((xv >> i) & 1) << (2 * i) | ((yv >> i) & 1) << (2 * i + 1)
               for i in range(9))


def header_tile(font=DEFAULT_FONT):
    # Same word-sprite recipe as the Z3.1 Intermission heading. The native
    # renderer supplies the cyan tint, shear and animation.
    face = ImageFont.truetype(str(font), 30 * 4)
    text = 'Intermission'
    l, t, r, b = face.getbbox(text)
    ink = Image.new('RGBA', (r - l, b - t))
    ImageDraw.Draw(ink).text((-l, -t), text, font=face, fill='white')
    ink = ink.resize((min(288, round(ink.width / 4)), 29), Image.Resampling.LANCZOS)
    tile = Image.new('RGBA', (296, 40))
    tile.alpha_composite(ink, ((296 - ink.width) // 2, 4))
    return tile


def apply_art(raw, font=DEFAULT_FONT):
    require(sha(raw) == ART_SHA, 'Rengoku Intermission atlas changed')
    root = Path(__file__).resolve().parents[1]
    message = json.loads((root / 'localization/locales/en/artwork.json').read_text(
        encoding='utf8'))['messages']['art:df993663e5cdef81a796']
    require(message['source'] == 'インターミッション' and message['text'] == 'Intermission',
            'Canonical Intermission heading changed')
    require(struct.unpack_from('>I', raw, 8)[0] == 4 and raw[24] == 0x85 and
            struct.unpack_from('>HH', raw, 32) == (512, 512), 'Intermission GTF layout')
    start = struct.unpack_from('>I', raw, 16)[0]
    out = bytearray(raw)
    tile = header_tile(font)
    allowed = set()
    for yy in range(40):
        for xx in range(296):
            r, g, b, a = tile.getpixel((xx, yy))
            pos = start + 4 * morton(xx, yy + 192)
            out[pos:pos + 4] = bytes((a, r, g, b))
            allowed.update(range(pos, pos + 4))
    require(all(a == b or i in allowed for i, (a, b) in enumerate(zip(raw, out))),
            'Unrelated atlas pixels changed')
    return bytes(out)


def review(source):
    """Consecutive 80-record slices and five context records on each side."""
    start, end = struct.unpack_from('>II', source, 0x48)
    slices = sorted({((row - start) // 32) // 80 for row in set(LABELS) | set(FOOTER_STATS)})
    examined, rows = set(), []
    for block in slices:
        lo = start + block * 80 * 32
        hi = min(end, lo + 80 * 32)
        for row in range(max(start, lo - 5 * 32), min(end, hi + 5 * 32), 32):
            examined.add(row)
            rows.append({'slice': block, 'row': hex(row),
                         'source': field(source, row).decode('cp932'),
                         'display': LABELS.get(row, (None, None))[1],
                         'context': not lo <= row < hi})
    return {'slices': slices, 'in_slice_records': len(slices) * 80,
            'unique_records_examined': len(examined), 'rows': rows,
            'terminology': 'MEL/DEF reuse existing abbreviations; complete PP and training labels; Intermission from canonical artwork.',
            'unresolved_translation_choices': []}
