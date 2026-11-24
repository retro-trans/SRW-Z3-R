"""Keep native battle buffers Japanese; translate only at the owned draw lookup.

NPJB00689 copies converted subtitles into 0x86-byte object buffers. English
atlas text is two bytes per letter and must never be copied into those fields.
"""
import struct
from collections import defaultdict
from rengoku_runtime import require,sha

NATIVE_CAPACITY=0x86

def guard(original):
    # Native converter, four callers, buffer initialization, and a second
    # fixed-size copy into the animation UI. Addresses are Rengoku's own VAs.
    for va,expected in (
        (0x12c088,0x38630fb3),(0x12c0a0,0x38a00086),
        (0x12c4a0,0x4bffff15),(0x12de04,0x4bffe5b1),
        (0x12decc,0x4bffe4e9),(0x12e11c,0x4bffe299),
        (0x14800c,0x38a00086)):
        require(struct.unpack_from('>I',original,va-0x10000)[0]==expected,
                'Battle caption consumer changed: '+hex(va))

def draw_hooks(codec,occurrences,display):
    candidates=defaultdict(set);sources=[];overflow=[]
    for row in occurrences:
        if not isinstance(row.get('bank'),int):continue
        native=row['jp'].replace('\\n','\n').encode('cp932')
        require(len(native)+1<=NATIVE_CAPACITY,'Original subtitle exceeds native field')
        target=codec.encode(display[row['offset']].replace('\\n','\n'))
        candidates[native].add(target)
        sources.append(row)
        if len(codec.encode(row['english'].replace('\\n','\n')))+1>NATIVE_CAPACITY:
            overflow.append(row['id'])
    require(all(len(values)==1 for values in candidates.values()),
            'Ambiguous native battle caption lookup')
    hooks={key:next(iter(values)) for key,values in candidates.items()}
    report=dict(native_capacity=NATIVE_CAPACITY,native_source_occurrences=len(sources),
        native_source_max_bytes=max(len(r['jp'].replace('\\n','\n').encode('cp932'))+1 for r in sources),
        converted_draw_keys=len(hooks),previous_unsafe_english_occurrences=len(overflow),
        previous_unsafe_occurrence_ids=overflow,
        english_storage='owned draw lookup; never copied into native subtitle/state objects',
        srvc_and_cue_metadata_preserved=True,gameplay_tested=False)
    return hooks,report
