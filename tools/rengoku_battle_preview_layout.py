"""Compact NPJB00689 battle-preview captions; preserve all live value fields."""
import struct

from rengoku_runtime import require
from rengoku_search_layout import field
from rengoku_screenshot_layout import line_width
from rengoku_roster_settings_layout import x

STYLE_ASSET = 'work/pkg/USRDIR/DATA_REN/AIDDATA/AIDDATAPACK_R.CPK:4'

# These are Rengoku's own records. Shared attack/weapon widgets cover both
# factions and main/support slots. Canonical translations remain unabridged.
LABELS = {
    0x8ae64: ('攻撃', 'Atk.'),
    0xa0364: ('援護攻撃', 'S. Atk'),
    0xa0384: ('再攻撃', 'Re-Atk'),
    0xa03a4: ('援護防御', 'S. Def'),
    0xa03e4: ('気力', 'Foc'),
    0xa0424: ('気力', 'Foc'),
    0xa0444: ('攻撃', 'Atk.'),
    0xa05c4: ('防御', 'Def.'),
    0xa05e4: ('援防', 'S.D.'),
    0xa70e4: ('残弾数', 'Rnd.'),
    0xa7164: ('ＥＮ', 'EN'),
    0xa7184: ('消費', ''),
    0xa71c4: ('歌', 'S.EN'),
    0xa71e4: ('消費', ''),
    0xa7224: ('ＥＮ', ''),
}
ACTION_ROWS = (0x8ae64, 0xa0444, 0xa05c4, 0xa05e4)
SUPPORT_ROWS = (0xa0364, 0xa0384, 0xa03a4)
FOCUS_ROWS = (0xa03e4, 0xa0424)
# Anchor labels to their real colon records instead of estimating a whole
# panel width. Charges already fits and is checked without modifying it.
COLONS = {0xa70e4: 0xa7104, 0xa7144: 0xa7124,
          0xa7164: 0xa71a4, 0xa71c4: 0xa7204}
PRESETS = {2: (25, 25, 23, 25, 25, 25, 23, 25),
           4: (23, 23, 21, 23, 23, 23, 21, 23),
           9: (37, 37, 0, 0, 0, 0, 0, 0)}


def preset_quad(styles, index):
    require(struct.unpack_from('>I', styles, 0x484)[0] == 13,
            'Battle preview font preset count changed')
    values = struct.unpack_from('>8h', styles, 0x488 + index * 16)
    require(values == PRESETS[index], 'Battle preview font preset changed')
    return values[0]


def apply_fssa(source, built, codec, styles):
    out = bytearray(built)
    base = struct.unpack_from('>I', source, 0x20)[0]
    report = []
    for row, (jp, display) in sorted(LABELS.items()):
        require(field(source, row) == jp.encode('cp932'),
                'Battle preview source label ' + hex(row))
        preset = 9 if row in ACTION_ROWS else 2 if row in FOCUS_ROWS else 4
        require(source[row + 22] & 15 == preset,
                'Battle preview row preset ' + hex(row))
        # Glyph size comes from the font preset. Record bytes 16..21 are
        # character pitches, which are deliberately different in this UI.
        quad = preset_quad(styles, preset)
        width = line_width(codec, display, quad)
        if row in ACTION_ROWS:
            limit = 86  # 94px badge, reserving 8px for italic ink/arrow
        elif row in SUPPORT_ROWS:
            limit = 84  # counter begins 96px after the title; reserve 12px
        elif row in FOCUS_ROWS:
            limit = 48  # 56px before three-digit value, with an 8px gap
        elif row in COLONS:
            colon = COLONS[row]
            require(field(source, colon) == '：'.encode('cp932'),
                    'Battle preview colon changed')
            limit = x(source, colon) - x(source, row) - 4
        else:
            limit = 0  # redundant EN-cost fragments now intentionally blank
        require(width <= limit, 'Battle preview caption exceeds slot ' + hex(row))
        dest = len(out)
        out.extend(codec.encode(display) + b'\0')
        struct.pack_into('>I', out, row, dest - base)
        report.append({'row': hex(row), 'source': jp, 'display': display,
                       'font_preset': preset, 'glyph_quad': quad,
                       'width': width, 'width_limit': limit,
                       'position_style_and_values_preserved': True})
    # The charge alternative shares the weapon strip. Keep its full wording
    # because it clears its separate colon without squeezing the font.
    require(field(source, 0xa7144) == 'チャージ数'.encode('cp932'), 'Charge label source')
    require(field(built, 0xa7144) == codec.encode('Charges'), 'Charge label translation')
    require(line_width(codec, 'Charges', preset_quad(styles, 4)) + 4 <=
            x(source, COLONS[0xa7144]) - x(source, 0xa7144), 'Charge label overlaps colon')
    allowed = {p for row in LABELS for p in range(row, row + 4)}
    require(all(a == b or p in allowed for p, (a, b) in enumerate(zip(built, out))),
            'Unlisted battle-preview edit')
    return bytes(out), report
