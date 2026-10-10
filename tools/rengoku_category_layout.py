"""Measured Rengoku skill, bonus and operation-condition presentation."""
import re
import struct
from rengoku_runtime import require
from rengoku_search_layout import field
from rengoku_screenshot_layout import line_width

SKILL_WIDTH = 760
SKILL_QUAD = 32
STORY_WIDTH = 870


def wrap(codec, text, width, quad=32):
    result, line = [], ''
    for word in text.split():
        trial = (line + ' ' + word).strip()
        if line and line_width(codec, trial, quad) > width:
            result.append(line); line = word
        else:
            line = trial
        require(line_width(codec, line, quad) <= width, 'Word exceeds display bounds')
    if line: result.append(line)
    require(' '.join(result).split() == text.split(), 'Wrapping changed words')
    return '\n'.join(result)


def operation_spans(text):
    # All operation messages stay Japanese in the native processing buffers.
    # Lookup supplies English only when drawn, in owned, unbounded storage.
    return [(m.start(1), m.end(1)) for m in re.finditer(
        r'OPERATE_TBL\s*=\s*\{\s*str_tbl\s*=\s*\{(.*?)\}\s*;', text, re.S)]


def bonus_hooks(rows, codec):
    hooks, report = {}, []
    for r in rows:
        if r['asset']!='work/eboot/EBOOT.ELF':continue
        if not (0x83216e<=r['offset']<=0x832334 or 0x880bd0<=r['offset']<=0x880d38):continue
        display=wrap(codec,r['english'],1070)
        require(len(display.split('\n'))<=2,'Bonus effect exceeds two rows')
        hooks[r['jp'].encode('cp932')]=codec.encode(display)
        report.append({'id':r['id'],'display':display,'line_widths':[
            line_width(codec,s,32) for s in display.split('\n')]})
    return hooks,report


def apply_fssa(source, built, codec):
    out = bytearray(built); base = struct.unpack_from('>I', source, 32)[0]
    labels = {
        0x8bde4: ('：カスタムボーナス', ': Custom Bonus', 551.5, 210),
        0x8bea4: ('：カスタム', ': Custom Bonus', 551.5, 210),
        0x99844: ('：カスタム', ': Custom Bonus', 551.5, 210),
        0x99884: ('：フル改造ボーナス', ': Full Upgrade Bonus', 551.5, 210),
        0x8bee4: ('カスタムボーナスを獲得しました。', 'Custom Bonus obtained.', 671.5, 700),
        0x9a004: ('カスタムボーナスを獲得しました。', 'Custom Bonus obtained.', 671.5, 700),
        # The yellow text is a static placeholder behind the live notification.
        0x8bf04: ('カスタムボーナス', '', 527.5, 700),
        0x9a024: ('カスタムボーナス', '', 559.5, 700),
    }
    allowed, report = set(), []
    for p, (jp, en, left, limit) in labels.items():
        require(field(source, p).decode('cp932') == jp, 'Bonus source changed')
        dest = len(out); out.extend(codec.encode(en) + b'\0')
        struct.pack_into('>I', out, p, dest - base); allowed.update(range(p, p+4))
        quad = source[p+19]
        while line_width(codec, en, quad) > limit: quad -= 1
        require(quad >= 15, 'Bonus caption requires excessive condensation')
        out[p+19] = quad; allowed.add(p+19)
        if p in (0x8bea4, 0x99844):
            # The original header's ボーナス tail is a second physical record.
            q = p+32
            require(field(source, q).decode('cp932') == 'ボーナス', 'Bonus tail changed')
            empty = len(out); out.extend(b'\0'); struct.pack_into('>I', out, q, empty-base)
            allowed.update(range(q, q+4))
        report.append({'row': hex(p), 'source': jp, 'display': en,
                       'quad': quad, 'width': line_width(codec, en, quad), 'limit': limit})
    require(all(a == b or i in allowed for i, (a,b) in enumerate(zip(built,out))),
            'Unexpected bonus metadata change')
    return bytes(out), report
