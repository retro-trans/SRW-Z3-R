"""Timed Rengoku narration: owned text, unchanged rows/cues, measured bounds."""
import struct
from rengoku_runtime import require,sha
from rengoku_screenshot_layout import line_width

HEADERS={13:'00473001262b263c0ce00078000000003f36db6e',
         14:'00313603262b263c0ce00078000000003f36db6e'}
GROUPS={13:((4,8),(19,25),(26,31),(43,49),(65,69)),14:((4,7),(23,25),(45,47))}
LEFT=96
WIDTH=1088
QUAD=32


def apply(raw,rows,codec,member):
    require(raw[:20].hex()==HEADERS[member],'Narration header changed')
    count=struct.unpack_from('>H',raw)[0];stride=raw[2]+30
    require(len(raw)==20+count*stride,'Narration record extent changed')
    byindex={}
    for r in rows:
        i,rem=divmod(r['offset']-20,stride)
        require(not rem and 0<=i<count,'Narration row binding')
        require(raw[r['offset']:raw.index(0,r['offset'])].decode('cp932')==r['jp'],'Narration source')
        byindex[i]=r
    expected={i for a,b in GROUPS[member] for i in range(a,b)}
    require(set(byindex)==expected,'Narration coverage changed')
    display={i:r['english'] for i,r in byindex.items()}
    # Layout-only changes: retain every word and the number of timed rows.
    if member==13:
        display[5]='Existing in separate spacetimes, they were called'
        display[6]='parallel worlds, and were never meant to intersect.'
        display[45]='Enclosed by a dimensional barrier created by the alien'
        display[46]='Geminaids, it had become a Prison of Time.'
    for a,b in GROUPS[member]:
        require(' '.join(display[i] for i in range(a,b)).split()==
                ' '.join(byindex[i]['english'] for i in range(a,b)).split(),
                'Narration reflow changed wording')
    hooks={};report=[]
    for i,r in sorted(byindex.items()):
        text=display[i];width=line_width(codec,text,QUAD)
        require('\n' not in text and width<=WIDTH,'Narration exceeds safe width: '+text)
        hooks[r['jp'].encode('cp932')]=codec.encode(text)
        report.append({'id':r['id'],'row':i,'display':text,'width':width})
    out=bytearray(raw)
    # Rengoku VA 0x58e2c..0x58e84 passes header +4,+5,+6,+7 to
    # 0x13884: glyph width, height, advance, row pitch. 0x58f4c reads
    # unsigned byte +9 as x, passed through 0x58ad8 to draw at 0x58c48.
    # Keep +7=60 and all record/scroll/timing bytes exactly as supplied.
    out[4:7]=bytes((QUAD,36,QUAD));out[9]=LEFT
    require(out[20:]==raw[20:],'Narration commands changed')
    return bytes(out),hooks,{'member':member,'source_sha256':sha(raw),
            'left':LEFT,'right':LEFT+WIDTH,'quad':[QUAD,36],
            'row_pitch':60,'rows':report,'timing_and_records_preserved':True}
