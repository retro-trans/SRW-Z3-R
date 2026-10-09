"""Fit the fast-forward prompt before the adjacent Cancel button icon."""
import struct

from rengoku_runtime import require
from rengoku_search_layout import field
from rengoku_screenshot_layout import line_width

STYLE_ASSET = 'work/pkg/USRDIR/DATA_REN/AIDDATA/AIDDATAPACK_R.CPK:4'
ROWS = {0x8c2e4: (4, 23), 0x8c944: (6, 21)}
SOURCE = '：早送り'
DISPLAY = '：Fast'
PRESETS = {4: (23, 23, 21, 23, 23, 23, 21, 23),
           6: (21, 21, 18, 21, 21, 21, 18, 21)}


def apply_fssa(source, built, codec, styles):
    out = bytearray(built)
    base = struct.unpack_from('>I', source, 0x20)[0]
    require(struct.unpack_from('>I', styles, 0x484)[0] == 13,
            'Battle control font preset count changed')
    report = []
    for row, (preset, quad) in sorted(ROWS.items()):
        require(field(source, row) == SOURCE.encode('cp932'),
                'Fast-forward source ' + hex(row))
        require(source[row + 22] & 15 == preset,
                'Fast-forward row preset ' + hex(row))
        require(struct.unpack_from('>8h', styles, 0x488 + preset * 16) == PRESETS[preset],
                'Fast-forward font dimensions changed')
        # Stay within the original four Japanese cells, with an 8px reserve.
        # The short prompt retains the native colon, font and button positions.
        limit = len(SOURCE) * quad - 8
        width = line_width(codec, DISPLAY, quad)
        require(width <= limit, 'Fast-forward caption exceeds original span')
        ptr = len(out)
        out.extend(codec.encode(DISPLAY) + b'\0')
        struct.pack_into('>I', out, row, ptr - base)
        report.append({'row': hex(row), 'source': SOURCE, 'display': DISPLAY,
                       'font_preset': preset, 'glyph_quad': quad,
                       'width': width, 'width_limit': limit,
                       'style_and_button_positions_preserved': True})
    allowed = {p for row in ROWS for p in range(row, row + 4)}
    require(all(a == b or p in allowed for p, (a, b) in enumerate(zip(built, out))),
            'Unlisted battle-control edit')
    return bytes(out), report
