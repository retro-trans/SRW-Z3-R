"""Fit every fixed caption in the Rengoku Full Upgrade Bonus selector."""
import struct
from rengoku_runtime import require
from rengoku_search_layout import field
from rengoku_screenshot_layout import line_width

LABELS = {
    0x9a044: ('地形適応【空】\n地形適応【陸】\n移動力',
              'Terrain 【Air】\nTerrain 【Land】\nMovement',290),
    0x9a064: ('地形適応【海】\n地形適応【宇】\n\n強化パーツスロット\n',
              'Terrain 【Sea】\nTerrain 【Space】\n\nPart Slots\n',290),
    # Native live value starts at 508.5; caption starts at 183.5. Leave >=16px.
    0x9a084: ('バリア・アーマー消費ＥＮを半減する','Barrier/armor EN cost',309),
}


def apply(source,built,codec):
    out = bytearray(built);base = struct.unpack_from('>I',source,0x20)[0]
    allowed,proof = set(),[]
    for p,(jp,en,limit) in LABELS.items():
        require(field(source,p).decode('cp932')==jp,'Upgrade selector source changed')
        quad=source[p+19]
        widths=[line_width(codec,s,quad) for s in en.split('\n')]
        require(max(widths)<=limit,'Upgrade selector caption touches live value')
        require(len(en.split('\n'))==len(jp.split('\n')),'Selector row spacing changed')
        dest=len(out);out.extend(codec.encode(en)+b'\0')
        struct.pack_into('>I',out,p,dest-base);allowed.update(range(p,p+4))
        proof.append(dict(row=hex(p),display=en,quad=quad,line_widths=widths,limit=limit))
    require(all(a==b or i in allowed for i,(a,b) in enumerate(zip(built,out))),
            'Unexpected selector metadata change')
    return bytes(out),proof
