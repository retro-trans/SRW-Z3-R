"""Source-bound layout changes for the supplied NPJB00689 screenshots."""
import struct
import re
from rengoku_runtime import require,cell

TERRAIN={'空':'\ue100','陸':'\ue101','海':'\ue102','水':'\ue102',
         '宇':'\ue103','地':'\ue104'}


def text_for_field(jp,en):
    # Vertical unit terrain is ONE field with four lines, not four labels.
    # Preserve its native line spacing and single-cell column width.
    if jp and any(c in TERRAIN for c in jp) and all(c in TERRAIN or c=='\n' for c in jp):
        return ''.join(TERRAIN.get(c,c) for c in jp)
    return en


def line_width(codec,text,quad=30):
    return sum(codec.widths.get(cell(codec.codes[c]),32) if c in codec.codes else 32
               for c in text)*quad/32


def library_text(codec,tag,text):
    # Rengoku's own FSSA library ruler is 38 cells, with a 30px quad. The
    # native consumer expects explicit newlines; preserve paragraph breaks.
    if tag not in ('DSCR','DSC2'):return text
    lines=[]
    for paragraph in text.replace('\r\n','\n').split('\n'):
        line=''
        for word in paragraph.split(' '):
            candidate=line+' '+word if line else word
            if line and line_width(codec,candidate)>1140:
                lines.append(line);line=word
            else:line=candidate
            require(line_width(codec,line)<=1140,'Library word exceeds panel width: '+word)
        lines.append(line)
    result='\n'.join(lines)
    require(result.split()==text.split(),'Library wrapping changed content')
    return result


def chapter_hooks(codec,rows):
    # 0x1dabd4 formats 第 + fullwidth decimal + 話. 0x1dafc8 concatenates
    # that prefix, 『, the chapter title, and 』 in both native encodings.
    # Match only complete known titles; never replace text inside dialogue.
    offsets=(0x95a538,0x95a548,0x95a558,0x95a568,0x95a578,0x95a590,
             0x95a598,0x95a5b8,0x95a5c8,0x95a5e0,0x95a600,0x95a620,
             0x95a630,0x95a640,0x95a650)
    titles={r['jp']:r['english'] for r in rows
            if r['asset']=='work/eboot/EBOOT.ELF' and r['offset'] in offsets}
    require(len(titles)==15,'Missing Rengoku chapter title translation')
    result={}
    for jp,en in titles.items():
        for n in range(1,100):
            digits=''.join(chr(0xff10+int(c)) for c in str(n))
            key='第'+digits+'話『'+jp+'』'
            result[key.encode('cp932')]=codec.encode('Episode %d: %s'%(n,en))
        result[('最終話『'+jp+'』').encode('cp932')]=codec.encode('Final Episode: '+en)
    return result


def hooks(codec,messages):
    plain={v['source']:v['text'] for v in messages.values() if v.get('text')}
    result={jp.encode('cp932'):codec.encode(ch) for jp,ch in TERRAIN.items()}
    for jp in ('空陸海宇','空陸水地','空\n陸\n海\n宇'):
        result[jp.encode('cp932')]=codec.encode(text_for_field(jp,''))
    # UTF-8 stat labels pass through the normal draw lookup after conversion.
    for jp,en in [('格闘','MEL'),('射撃','RNG')]:result[jp.encode('cp932')]=codec.encode(en)
    # Cover the complete level-bearing skill category, including generated
    # levels and bonuses. The source composites identify additional spellings.
    level_names={jp:plain[jp] for jp in ('底力','援護攻撃','援護防御','ＳＰアップ',
        'カウンター','サイズ差補正無視','指揮官','ニュータイプ','強化人間',
        '超能力','螺旋力','念動力','プレッシャー')}
    for v in messages.values():
        if not v.get('text'):continue
        for jp,en in zip(v['source'].split('\n'),v['text'].split('\n')):
            a=re.fullmatch(r'(.+?)[ 　]?[ＬL][１-９1-9](?:[＋+][１-９1-9])?',jp)
            b=re.fullmatch(r'(.+?) L[1-9](?:\+[1-9])?',en)
            if a and b:level_names[a[1].strip()]=b[1]
    for jp,en in level_names.items():
        require('$$' not in en,'Resolve skill glossary before layout')
        for n in range(1,10):
            for separator in ('',' ','　'):
                for level in ('Ｌ','L'):
                    for digit in (str(n),chr(0xff10+n)):
                        result[(jp+separator+level+digit).encode('cp932')]=codec.encode(en+' L'+str(n))
        for n in range(1,10):
            for bonus in range(1,10):
                for full in (True,False):
                    digit=lambda x:chr(0xff10+x) if full else str(x)
                    suffix=('Ｌ' if full else 'L')+digit(n)+('＋' if full else '+')+digit(bonus)
                    result[(jp+suffix).encode('cp932')]=codec.encode(en+' L%d+%d'%(n,bonus))
    return result


def native_movement_fields(original,codec):
    result=[]
    # Independently located Rengoku tables used by the unit/robot movement
    # composer (e.g. strcat at 0x31ebd4). One native cell per terrain type.
    for base in (0x888ec8,0x889128):
        for i,jp in enumerate('空陸水地'):
            off=base+8*i;old=jp.encode('utf-8')+b'\0'
            require(original[off:off+len(old)]==old,'Native movement source')
            result.append((off,old,codec.encode(TERRAIN[jp],utf8=True)+b'\0','compact movement type'))
    for off,jp in [(0x888e98,'空専用'),(0x888ea8,'空水専用'),(0x888eb8,'水専用')]:
        old=jp.encode('utf-8')+b'\0';require(original[off:off+len(old)]==old,'Exclusive movement source')
        value=''.join(TERRAIN[c] for c in jp[:-2])+'\ue105'
        result.append((off,old,(codec.encode(value,utf8=True)+b'\0').ljust(len(old),b'\0'),'compact exclusive movement type'))
    return result


def apply_fssa(source,built,codec):
    out=bytearray(built);base=struct.unpack_from('>I',source,0x20)[0];allowed=set();report=[]
    def text(raw,p):
        q=base+struct.unpack_from('>I',raw,p)[0];return raw[q:raw.index(0,q)]
    def x(p,jp,new):
        require(text(source,p).decode('cp932')==jp,'Layout source '+hex(p))
        old=640+struct.unpack_from('>f',source,p+4)[0]*640
        struct.pack_into('>f',out,p+4,(new-640)/640);allowed.update(range(p+4,p+8))
        report.append({'row':hex(p),'source':jp,'old_x':old,'new_x':new})
    def replace(p,jp,en):
        require(text(source,p).decode('cp932')==jp,'Layout text source '+hex(p))
        dest=len(out);out.extend(codec.encode(en)+b'\0')
        struct.pack_into('>I',out,p,dest-base);allowed.update(range(p,p+4))
        report.append({'row':hex(p),'source':jp,'display':en})
    # The screenshot's Focus value starts at native x~520. Preserve its value.
    x(0x9d704,'気力',412.5)
    # All four map summary colons share the same right-side column.
    for p in (0x9a544,0x9a584,0x9a5a4):x(p,'：',1176.5)
    replace(0x9d784,'精神コマンド','Spirits')
    for p in (0x9d5c4,0x9dd64):replace(p,'気力','Foc')
    # The heading consists of FOUR physical FSSA records. Relocating each
    # fragment destroys the NUL-separated sequence a draw-time joiner needs.
    # Put the complete label in its first record; blank only the other three.
    for p,jp,en in [(0x8a664,'エ','Ace Bonus'),(0x8a684,'ース',''),
                    (0x8a6a4,'ボー',''),(0x8a6c4,'ナス','')]:replace(p,jp,en)
    # Keep Nick/CV left-aligned. Only condense the nickname label horizontally
    # so its ink ends before the fixed value column at x~485; keep its height.
    for p in (0x9cc84,0x9cea4,0x9cf24):
        require(text(source,p).decode('cp932')=='愛称' and source[p+19]==31,'Nickname style source')
        out[p+19]=27;allowed.add(p+19)
        require(415.5+line_width(codec,'Nick',27)<475,'Nickname overlaps value')
        report.append({'row':hex(p),'source':'愛称','glyph_width':27,'x_unchanged':True})
    replace(0x9ccc4,'：表情',': Face')
    # Shared italic kill-count suffix; increase its glyph quad to the count's
    # 31px style and retain its bottom edge while adding 10px separation.
    p=0x8f044;require(text(source,p).decode('cp932')=='機','Kill-count suffix source')
    require(source[p+16:p+22]==bytes.fromhex('191917191919'),'Kill-count suffix style')
    x(p,'機',825.5)
    for i,v in ((18,31),(19,31)):
        out[p+i]=v;allowed.add(p+i)
    struct.pack_into('>f',out,p+8,(361-360)/360);allowed.update(range(p+8,p+12))
    report.append({'row':hex(p),'source':'機','glyph_height':31,'glyph_width':31,'new_y':361})
    # Center the static information headings in the tabs observed in screenshots.
    for p,jp,en,center in [(0x90f24,'パイロット能力','Pilot Info',236),
                           (0x90f44,'パイロット能力','Pilot Info',236),
                           (0xa51c4,'パイロット能力','Pilot Info',236),
                           (0x90fa4,'武器性能','Weapon Info',400),
                           (0xa52c4,'武器性能','Weapon Info',400)]:
        width=sum(codec.widths[cell(codec.codes[c])] for c in en)*source[p+19]/32
        require(width<220,'Information heading does not fit');x(p,jp,center-width/2)
    require(all(a==b or i in allowed for i,(a,b) in enumerate(zip(built,out))),'Unlisted layout metadata edit')
    width=sum(codec.widths[cell(codec.codes[c])] for c in 'Focus')*31/32
    require(412.5+width<512,'Focus overlaps value')
    require(line_width(codec,'Spirits',28)<200,'Spirits overlaps next field')
    return bytes(out),report
