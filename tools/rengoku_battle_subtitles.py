"""Word-preserving layout for Rengoku's battle-animation subtitle panel.

This is a display transform, never a translation-catalog edit. Native SRVC
escapes are converted by NPJB00689 routine 0x12c3b4 before drawing. Keep at
most two rows and never enlarge a subtitle past the native 0x86-byte buffer.
Longer pre-existing translations are reported separately, not truncated.
"""
import re

from rengoku_runtime import require
from rengoku_screenshot_layout import line_width

WIDTH = 730
QUAD = 32  # Conservative bound for the ~31px quads in the supplied capture.
BUFFER_BYTES = 0x86
BREAK = '\\n'


def native_bytes(codec, text):
    return codec.encode(text.replace(BREAK, '\n')) + b'\0'


def fit(codec, text):
    """Keep fitting rows; otherwise choose a safe two-row word boundary."""
    require(not re.search(r'\$|%(?:\d+\$)?[-+#0]*(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|ll|[hljztL])?[diuoxXfFeEgGaAcsp%]|[\x00-\x09\x0b-\x1f]', text),
            'Battle subtitle needs runtime-substitution measurement')
    require('\\' not in text.replace(BREAK, ''), 'Unknown battle escape')
    rows = text.split(BREAK)
    require(len(rows) <= 2 and '\n' not in text, 'Unexpected SRVC line control')
    widths = [line_width(codec, row, QUAD) for row in rows]
    if max(widths) <= WIDTH:
        return text, None
    if len(native_bytes(codec, text)) > BUFFER_BYTES:
        return text, 'Existing English exceeds native intermediate buffer; relocation required'
    # Moving an existing visual break is allowed only in generated display
    # text. Words, punctuation, wrappers, glossary spelling and cue order stay.
    words = text.replace(BREAK, ' ').split()
    choices = []
    for k in range(1, len(words)):
        pair = [' '.join(words[:k]), ' '.join(words[k:])]
        widths = [line_width(codec, row, QUAD) for row in pair]
        if max(widths) > WIDTH:
            continue
        # Prefer an existing sentence/clause boundary, then balanced lines.
        clause = bool(re.search(r'[,;:!?\.]$', words[k - 1]))
        score = (not clause, abs(widths[0] - widths[1]))
        candidate = BREAK.join(pair)
        if len(native_bytes(codec, candidate)) <= BUFFER_BYTES:
            choices.append((score, candidate))
    if not choices:
        return text, 'Needs more than two rows at the current font size'
    result = min(choices)[1]
    require(result.replace(BREAK, ' ').split() == words,
            'Battle wrapping changed words or punctuation')
    return result, None


def layout(codec, occurrences):
    display = {}
    changed = []
    pending = []
    seen = set()
    for row in occurrences:
        if not isinstance(row.get('bank'), int):
            continue
        text, reason = fit(codec, row['english'])
        display[row['offset']] = text
        if row['message'] in seen:
            continue
        seen.add(row['message'])
        info = {'message': row['message'], 'bank': row['bank'],
                'cue_indexes': row['index_entries'], 'before': row['english']}
        if reason:
            pending.append(dict(info, reason=reason))
        elif text != row['english']:
            changed.append(dict(info, after=text,
                                widths=[line_width(codec, s, QUAD) for s in text.split(BREAK)],
                                native_bytes=len(native_bytes(codec, text))))
    report = {'unique_srvc_messages_examined': len(seen),
              'changed_unique_messages': len(changed),
              'changed_occurrences': sum(display[r['offset']] != r['english']
                  for r in occurrences if isinstance(r.get('bank'), int)),
              'width_px': WIDTH, 'conservative_quad_px': QUAD,
              'max_rows': 2, 'native_buffer_bytes': BUFFER_BYTES,
              'changed': changed, 'pending': pending}
    return display, report
