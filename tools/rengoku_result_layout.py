"""Compact kill totals in Rengoku's battle-results score column."""
import struct

from rengoku_runtime import require
from rengoku_search_layout import field
from rengoku_screenshot_layout import line_width
from rengoku_roster_settings_layout import x

# Score is two physical text records. Its counter uses the compact score
# widget's suffix, not Pilot Info's separately sized suffix at 0x8f044.
LABELS = {0x99ce4: ('Ｓｃｏ', 'Kills'),
          0x99d04: ('ｒｅ', ''),
          0xa6fe4: ('機', '')}
PILOT_SUFFIX = 0x8f044
LEVEL_HEADER = 0x99d24


def apply_fssa(source, built, codec):
    out = bytearray(built)
    base = struct.unpack_from('>I', source, 0x20)[0]
    require(field(source, LEVEL_HEADER) == 'Ｌｖ'.encode('cp932'),
            'Results level column changed')
    # The result header uses preset 1 (28px). Preserve its original style.
    require(source[0x99ce4 + 16:0x99ce4 + 24] ==
            bytes.fromhex('1c1c1a1c101c3100'), 'Results header style changed')
    width = line_width(codec, 'Kills', 28)
    require(x(source, 0x99ce4) + width + 12 < x(source, LEVEL_HEADER),
            'Kills heading overlaps Level')
    require(source[0xa6fe4 + 16:0xa6fe4 + 24] ==
            bytes.fromhex('1919171919192200'), 'Compact score suffix style changed')
    report = []
    for row, (jp, display) in sorted(LABELS.items()):
        require(field(source, row) == jp.encode('cp932'),
                'Results label source ' + hex(row))
        ptr = len(out)
        out.extend(codec.encode(display) + b'\0')
        struct.pack_into('>I', out, row, ptr - base)
        report.append({'row': hex(row), 'source': jp, 'display': display,
                       'style_position_and_values_preserved': True})
    allowed = {p for row in LABELS for p in range(row, row + 4)}
    require(all(a == b or p in allowed for p, (a, b) in enumerate(zip(built, out))),
            'Unlisted results edit')
    require(out[PILOT_SUFFIX:PILOT_SUFFIX + 32] == built[PILOT_SUFFIX:PILOT_SUFFIX + 32],
            'Pilot Info Units suffix changed')
    return bytes(out), report
