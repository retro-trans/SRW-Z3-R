"""Source-bound Ally/Enemy menu states: aligned labels and inactive tint."""
import struct

from rengoku_runtime import require
from rengoku_search_layout import field
from rengoku_screenshot_layout import line_width

# Each state draws two records. The slash belongs to the selected side.
STATES = (
    ((0x978e4, '味方部隊／', 'Ally /', True),
     (0x97904, '敵', 'Enemy', False)),
    ((0x97924, '味方', 'Ally', False),
     (0x97944, '／敵部隊', '/ Enemy', True)),
)
SOURCE_STYLES = (
    'a0a0ffff1c1c1a1c1c1c217c0000000010000000',
    'ffffffff151512151515127c0000000010000000',
    'a0a0ffff191917191919227c0000000010000000',
    'ffffffff1c1c1a1c1c1c117c0000000010000000',
)
QUAD, GAP, CENTER = 28, 10, 639.5
DIM = 96  # RGB multiplier / 255; keep alpha and native faction palette.


def apply_fssa(source, built, codec):
    out = bytearray(built)
    base = struct.unpack_from('>I', source, 0x20)[0]
    allowed, report = set(), []
    for state_index, state in enumerate(STATES):
        widths = [line_width(codec, item[2], QUAD) for item in state]
        require(sum(widths) + GAP < 200, 'Ally/Enemy row exceeds button')
        centers = (CENTER - (widths[1] + GAP) / 2,
                   CENTER + (widths[0] + GAP) / 2)
        for i, (row, jp, en, selected) in enumerate(state):
            require(field(source, row) == jp.encode('cp932'),
                    'Ally/Enemy source label ' + hex(row))
            require(source[row + 12:row + 32].hex() == SOURCE_STYLES[2 * state_index + i],
                    'Ally/Enemy source style ' + hex(row))
            ptr = len(out)
            out.extend(codec.encode(en) + b'\0')
            struct.pack_into('>Iff', out, row, ptr - base,
                             (centers[i] - 640) / 640,
                             struct.unpack_from('>f', source, 0x978e4 + 8)[0])
            # Match Z3.1's split-label geometry, using Rengoku records and
            # its own proportional centering adapter (no sibling addresses).
            out[row + 16:row + 22] = bytes((28, 28, 26, 28, 28, 28))
            allowed.update(range(row, row + 12))
            allowed.update(range(row + 16, row + 22))
            if not selected:
                # Native setup at 0x5f770 reads this RGBA word; draw at
                # 0x1423c multiplies it by the faction palette. Do not dim
                # that shared palette, which would affect selected labels.
                out[row + 12:row + 15] = bytes(v * DIM // 255 for v in source[row + 12:row + 15])
                allowed.update(range(row + 12, row + 15))
            report.append({'state': ('ally', 'enemy')[state_index],
                           'row': hex(row), 'source': jp, 'display': en,
                           'selected': selected, 'rgba': out[row + 12:row + 16].hex(),
                           'center_x': centers[i], 'width': widths[i],
                           'glyph_quad': QUAD, 'gap': GAP})
    require(all(a == b or p in allowed for p, (a, b) in enumerate(zip(built, out))),
            'Unlisted Ally/Enemy menu edit')
    return bytes(out), report
