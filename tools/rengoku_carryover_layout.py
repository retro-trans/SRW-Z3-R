"""Rengoku carryover variants: complete prose, separate labels and live rates."""
import struct
from rengoku_runtime import require
from rengoku_search_layout import field
from rengoku_screenshot_layout import line_width

INTRO_JP='今回のプレイで入手した資金・Ｚチップ・ＰＰ・撃墜数を引き継いでゲームを開始します。'
INTRO='Start a new game with funds, Z Chips, PP and kills earned this run.'
NO_Z_JP='今回のプレイで入手した資金・ＰＰ・撃墜数を引き継いでゲームを開始します。'
NO_Z='Start a new game with funds, PP and kills earned this run.'
RATES_JP='資金・Ｚチップ・ＰＰは、以下の引継ぎになります。'
RATES='Funds, Z Chips and PP carry over at these rates:'
NO_Z_RATES_JP='資金・ＰＰは、以下の引継ぎになります。'
NO_Z_RATES='Funds and PP carry over at these rates:'
UPGRADE_JP='　　　　　　また、４周目以降は機体・武器の改造限界が１５段階になります。'
UPGRADE='From run 4, units and weapons can be upgraded to level 15.'
LABEL_JP='「２周目　：　　　　　」\n「３周目　：　　　　　」\n「４周目～：　　　　　」'
LABEL='2nd run:\n3rd run:\n4th run onward:'
VALUES='　５０％\n　７５％\n１００％'
PARTS_JP='１周クリアに付き、クリア時に所持している強化パーツを５個\n持ち越す事が出来ます（最大２５個　エンブレム系は除く）。'
PARTS='Per completed run, carry over 5 Power Parts owned at clear.\nMaximum: 25 total; Emblems excluded.'

def indexed_text(jp,en):
    return {NO_Z_JP:NO_Z,NO_Z_RATES_JP:NO_Z_RATES}.get(jp,en)

def apply_fssa(source,built,codec):
    out=bytearray(built);base=struct.unpack_from('>I',source,32)[0]
    replacements={
        0x99304:(INTRO_JP,INTRO),0x99324:(RATES_JP,RATES),
        0x99a44:('【　　　　】',''),0x99a64:('周回特典','Carryover'),
        0x9a1e4:(UPGRADE_JP,UPGRADE),0x9a204:('改造限界が１５段階',''),
        0x9a224:(LABEL_JP,LABEL),0x9a264:(PARTS_JP,PARTS),
        0x9a284:('強化パーツを５個',''),
        0x9a2a4:(INTRO_JP+'\n'+UPGRADE_JP,INTRO+'\n'+UPGRADE),
        0x9a2c4:('改造限界が１５段階',''),0x9a2e4:(RATES_JP,RATES),
        0x9a304:(LABEL_JP,LABEL),0x9a344:(PARTS_JP,PARTS),0x9a364:('強化パーツを５個','')}
    x_positions={0x9a224:400,0x9a304:400,0x9a244:760,0x9a324:760,
                 0x9a264:191.5,0x9a344:191.5}
    allowed=set();report=[]
    for row,(jp,text) in replacements.items():
        require(field(source,row)==jp.encode('cp932'),'Carryover source changed: '+hex(row))
        quad=source[row+19];widths=[line_width(codec,s,quad) for s in text.split('\n')]
        limit=150 if row==0x99a64 else (260 if row in (0x9a224,0x9a304) else 1050)
        require(max(widths,default=0)<=limit,'Carryover caption exceeds panel')
        p=len(out);out.extend(codec.encode(text)+b'\0');struct.pack_into('>I',out,row,p-base)
        allowed.update(range(row,row+4))
        report.append(dict(row=hex(row),source=jp,display=text,quad=quad,line_widths=widths,width_limit=limit))
    for row in (0x9a244,0x9a324):
        require(field(source,row)==VALUES.encode('cp932'),'Carryover percentages changed')
        require(field(built,row)==field(source,row),'Carryover live percentages must stay native')
    for row,new_x in x_positions.items():
        struct.pack_into('>f',out,row+4,(new_x-640)/640);allowed.update(range(row+4,row+8))
    for label,amount in ((0x9a224,0x9a244),(0x9a304,0x9a324)):
        label_end=400+max(line_width(codec,s,source[label+19]) for s in LABEL.split('\n'))
        require(not source[amount+23]&0x40,'Carryover percentage alignment changed')
        value_left=760
        require(value_left-label_end>=80,'Carryover labels touch percentages')
        report.append(dict(row=hex(amount),display=VALUES,live_values_preserved=True,
                           label_right=label_end,value_left=value_left,gap=value_left-label_end))
    require(all(a==b or i in allowed for i,(a,b) in enumerate(zip(built,out))),
            'Unlisted carryover metadata change')
    return bytes(out),report
