"""Measured English credits columns; preserve all native scrolling commands."""
import re
from rengoku_runtime import require,sha
from rengoku_screenshot_layout import line_width
from non_dialogue import credit_fields

HEADER = '01b740002424242a0c4000f0000500003fe5be5c'
LEFT, WIDTH, RIGHT_COLUMN = 64, 1120, 640


def format_row(codec,text,quad):
    require('\n' not in text,'Credits row contains a newline')
    leading = len(text)-len(text.lstrip('\u3000'))
    parts = re.split('\u3000{2,}',text.lstrip('\u3000').rstrip())
    require(len(parts)<=2,'Unverified additional credit column')
    space = line_width(codec,' ',quad)
    require(space>0,'Credit space has no advance')
    indent = ' '*round(leading*quad/space)
    if len(parts)==2:
        left = indent+parts[0]
        gap = max(32,RIGHT_COLUMN-line_width(codec,left,quad))
        result = left+' '*round(gap/space)+parts[1]
    else:
        result = indent+parts[0].replace('\u3000',' ')
    require(result.split()==text.split(),'Credits layout changed words')
    return result


def apply(raw,rows,codec):
    require(raw[:20].hex()==HEADER,'Credits header changed')
    fields = dict(credit_fields(raw))
    bound = {r['offset']:r for r in rows if r['offset'] in fields}
    require(set(fields)==set(bound),'Incomplete credits category')
    for p,r in bound.items():
        require(fields[p]==r['jp'],'Credits source changed')
    quad = 32
    while quad>=24:
        display = {p:format_row(codec,r['english'],quad) for p,r in bound.items()}
        if all(line_width(codec,s,quad)<=WIDTH for s in display.values()):break
        quad-=1
    require(quad>=24,'Credits require an independently verified wider layout')
    hooks,proof = {},[]
    for p,r in sorted(bound.items()):
        text = display[p]
        hooks[r['jp'].encode('cp932')] = codec.encode(text)
        proof.append(dict(id=r['id'],offset=p,display=text,width=line_width(codec,text,quad)))
    out = bytearray(raw)
    # Shared Rengoku reader: header +4/+5/+6/+7 are width/height/advance/pitch;
    # +9 is x. The native record count, 64-byte text fields, commands and pitch
    # remain identical. Text is translated in owned storage at display time.
    out[4]=quad;out[6]=quad
    require(out[20:]==raw[20:],'Credits rows or commands changed')
    return bytes(out),hooks,dict(source_sha256=sha(raw),quad=quad,left=LEFT,
        right=LEFT+WIDTH,right_column=LEFT+RIGHT_COLUMN,row_pitch=raw[7],
        native_records_preserved=True,rows=proof)
