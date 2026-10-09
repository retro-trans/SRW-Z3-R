"""Rengoku-only text codec, font generation and guarded PPU runtime patch.

Addresses below were derived from NPJB00689's authenticated program ELF and
disassembled locally. They are not Jigoku build addresses. No file I/O writes
occur in this module. The caller owns new output files and source preservation.
"""
import hashlib
import math
import re
import struct
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops
from fontTools.ttLib import TTFont

ELF_SHA = 'f8c669e088968924f33b61405ca800cd7acd8b0d02eac8a217c1b19b9a2a6131'
PH = struct.Struct('>IIQQQQQQ')
SH = struct.Struct('>IIQQQQIIQQ')
DRAW = 0x14158
ADVANCE = 0x147dc
KW_POSITION = 0x21cdf0
KW_ACC = 0x21e0d4
KW_CALLS = (0x21e1ec, 0x21e388, 0x21e560, 0x21e65c)
UNICODE_TABLE = 0x80f380
CODE = 0x8fb500
WIDTHS = 0x8fe000
SCRATCH = 0xce9000
TEXT = 0xcf0000
FONT_CELLS = 4480
DEFAULT_FONT = Path('E:/RPCS3/dev_flash/data/font/SCE-PS3-RD-B-LATIN.TTF')
COMPACT_LABELS = {'\ue100':'Air','\ue101':'Grd','\ue102':'Wtr','\ue103':'Spc',
                  '\ue104':'Und','\ue105':'Only'}
SPIRIT_LABELS = dict(zip((chr(0xe110 + i) for i in range(18)),
                        ('Va','So','Fs','Al','Wa','Gu','Fo','St','Ac','Ze',
                         'Me','Sn','As','Fu','Lu','Ga','Di','An')))
CHOICE_PAD = '\ue160'


def rodin_spirit(path, text):
    """Two-letter status cells: Z3.1 cap 16, baseline 23, 2px ink gap."""
    probe = ImageFont.truetype(str(path), 100)
    box = probe.getbbox('H', anchor='ls')
    face = ImageFont.truetype(str(path), round(100 * 16 / (box[3] - box[1]) * 4))
    parts = []
    for ch in text:
        l, t, r, b = face.getbbox(ch, anchor='ls')
        im = Image.new('L', (r - l + 9, b - t + 8))
        ImageDraw.Draw(im).text((4 - l, 4 - t), ch, font=face, fill=255, anchor='ls')
        im = ImageChops.lighter(im, ImageChops.offset(im, 1, 0))
        im = im.resize((max(1, round(im.width / 4)), max(1, round(im.height / 4))), Image.Resampling.BOX)
        crop = im.getbbox()
        require(crop is not None, 'Empty Spirit status letter')
        parts.append((im.crop(crop), round(23 + t / 4 - 1 + crop[1])))
    natural = sum(im.width for im, _ in parts)
    budget = min(natural, 28 - 2 * (len(parts) - 1))
    tile = Image.new('L', (32, 32))
    x = (32 - budget - 2 * (len(parts) - 1)) // 2
    total = previous = 0
    for im, y in parts:
        total += im.width
        edge = round(total * budget / natural)
        width = edge - previous
        previous = edge
        tile.paste(im.resize((width, im.height), Image.Resampling.BOX), (x, y))
        x += width + 2
    return tile


def rodin_compact(path, text):
    """Z3.1 terrain recipe: cap 11, baseline 20, natural letters, +0.3 stems."""
    probe=ImageFont.truetype(str(path),100)
    box=probe.getbbox('H',anchor='ls')
    face=ImageFont.truetype(str(path),round(100*11/(box[3]-box[1])*4))
    parts=[]
    for ch in text:
        l,t,r,b=face.getbbox(ch,anchor='ls')
        im=Image.new('L',(r-l+9,b-t+8))
        ImageDraw.Draw(im).text((4-l,4-t),ch,font=face,fill=255,anchor='ls')
        im=ImageChops.lighter(im,ImageChops.offset(im,1,0))
        im=im.resize((max(1,round(im.width/4)),max(1,round(im.height/4))),Image.Resampling.BOX)
        parts.append((im,l/4-1,t/4-1,face.getlength(ch)/4+0.25))
    tile=Image.new('L',(32,32));x=(32-sum(p[3] for p in parts))/2
    for im,l,t,advance in parts:
        # Match the reference renderer's maximum-coverage blit.
        layer=Image.new('L',(32,32));layer.paste(im,(round(x+l),round(20+t)))
        tile=ImageChops.lighter(tile,layer);x+=advance
    return tile


def rodin_glyph(path, ch):
    """Z3.1 natural-letter recipe: 22px cap, baseline 26, 4x SS, +0.5px stems."""
    probe=ImageFont.truetype(str(path),100)
    box=probe.getbbox('H',anchor='ls');size=100*22/(box[3]-box[1])
    face=ImageFont.truetype(str(path),round(size*4))
    advance=face.getlength(ch)/4+0.5
    if ch==' ':return Image.new('L',(32,32)),9
    l,t,r,b=face.getbbox(ch,anchor='ls')
    im=Image.new('L',(r-l+10,b-t+8))
    ImageDraw.Draw(im).text((4-l,4-t),ch,font=face,fill=255,anchor='ls')
    original=im.copy()
    for dx in (1,2):im=ImageChops.lighter(im,ImageChops.offset(original,dx,0))
    im=im.resize((max(1,round(im.width/4)),max(1,round(im.height/4))),Image.Resampling.BOX)
    cell_image=Image.new('L',(32,32))
    cell_image.paste(im,(round(l/4-1),round(26+t/4-1)))
    return cell_image,max(1,min(63,round(advance+1)))


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def align(n, a=16):
    return (n+a-1)//a*a


def cell(code):
    return ((code >> 8)-0x81)*192+(code & 255)-0x40


def font_pages(cpk):
    pages = {}
    for e in cpk.files:
        # These two pages are independently checked against the GTF headers.
        if e['id'] not in (1, 3):
            continue
        b = cpk.read(e)
        require(len(b) == 128+4096*1120*2 and b[0x18] == 0xab and
                struct.unpack_from('>HH', b, 0x20) == (4096, 1120),
                'Unexpected Rengoku font page')
        require(struct.unpack_from('>I', b, 16)[0] == 128, 'Font payload offset')
        pages[e['id']] = b
    require(set(pages) == {1, 3}, 'Both Rengoku font pages required')
    return pages


class Codec:
    def __init__(self, texts, pages, font_path):
        # Native punctuation and all runtime markers keep their original codes.
        want = set(''.join(texts))
        latin = sorted(c for c in want if ' ' <= c <= '~' or
                       c in 'é©®Ⓡ℠™–—¥')
        pool = []
        for code in range(0x8140, 0x9900):
            if not 0x40 <= (code & 255) <= 0xfc or (code & 255) == 0x7f:
                continue
            try:
                struct.pack('>H',code).decode('cp932')
                continue  # Includes the native ideographic space: never take it.
            except UnicodeDecodeError:
                pass
            i = cell(code)
            if not 0 <= i < FONT_CELLS:
                continue
            # Only truly empty cells in BOTH original pages are eligible.
            x, y = (i % 128)*32, (i//128)*32
            if all(not any(b[128+((y+dy)*4096+x)*2:
                                 128+((y+dy)*4096+x+32)*2])
                   for b in pages.values() for dy in range(32)):
                pool.append(code)
        require(len(pool) >= len(latin)+len(COMPACT_LABELS)+len(SPIRIT_LABELS)+1, 'Not enough unused Rengoku font cells')
        self.codes = dict(zip(latin, pool))
        self.reverse = {v:k for k,v in self.codes.items()}
        self.unicode = {c:0xe000+i for i,c in enumerate(latin)}
        font_path=Path(font_path)
        cmap=TTFont(str(font_path)).getBestCmap()
        fallback_path=Path('C:/Windows/Fonts/seguisym.ttf')
        fallback_cmap={}
        self.font_sources={font_path.name:sha(font_path.read_bytes())}
        self.glyphs, self.widths = {}, {}
        for ch, code in self.codes.items():
            selected=font_path
            if ord(ch) not in cmap:
                require(fallback_path.exists(),'Missing font glyph and symbol fallback: '+repr(ch))
                if not fallback_cmap:
                    fallback_cmap=TTFont(str(fallback_path)).getBestCmap()
                    self.font_sources[fallback_path.name]=sha(fallback_path.read_bytes())
                require(ord(ch) in fallback_cmap,'Missing symbol glyph: '+repr(ch))
                selected=fallback_path
            im,width=rodin_glyph(selected,ch)
            self.glyphs[code], self.widths[cell(code)] = im, width
        # Fixed terrain slots need one complete word per native character.
        for i,(ch,label) in enumerate(COMPACT_LABELS.items()):
            code=pool[len(latin)+i];self.codes[ch]=code;self.reverse[code]=ch
            self.unicode[ch]=ord(ch)
            self.glyphs[code]=rodin_compact(font_path,label);self.widths[cell(code)]=32
        for i, (ch, label) in enumerate(SPIRIT_LABELS.items()):
            code = pool[len(latin) + len(COMPACT_LABELS) + i]
            self.codes[ch] = code; self.reverse[code] = ch; self.unicode[ch] = ord(ch)
            self.glyphs[code] = rodin_spirit(font_path, label)
            self.widths[cell(code)] = 32  # preserve native one-cell status pitch
        code = pool[len(latin) + len(COMPACT_LABELS) + len(SPIRIT_LABELS)]
        self.codes[CHOICE_PAD] = code; self.reverse[code] = CHOICE_PAD
        self.unicode[CHOICE_PAD] = ord(CHOICE_PAD)
        self.glyphs[code] = Image.new('L', (32, 32))
        # This blank cell is a tab to column three, intercepted by the
        # advance adapter. Confirmation style 1 draws 28px quads at 25px
        # native pitch; a fixed proportional spacer cannot restore columns.
        self.widths[cell(code)] = 32
        self.pages = pages

    def encode(self, text, utf8=False, newline='\n'):
        text = text.replace('\r\n','\n').replace('\r','\n')
        out = bytearray()
        i = 0
        while i < len(text):
            c = text[i]
            # Placeholder bytes are interpreted before the font renderer.
            m = re.match(r'\$[A-Za-z]|\\[nr]|%(?:\d+\$)?[-+#0]*(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|ll|[hljztL])?[diuoxXfFeEgGaAcsp%]|【(?:必要容量|チェック容量|セーブデータ|セーブデータ詳|PS3改行|VITA改行|ストレージ|動作)】', text[i:])
            if m:
                out += m[0].encode('utf-8' if utf8 else 'cp932')
                i += len(m[0]); continue
            if c == '\n':
                out += newline.encode('ascii')
            elif 0 < ord(c) < 32:
                out.append(ord(c))
            elif c in self.codes:
                out += (chr(self.unicode[c]).encode('utf-8') if utf8 else
                        struct.pack('>H', self.codes[c]))
            else:
                raw = c.encode('utf-8' if utf8 else 'cp932')
                require(utf8 or len(raw)==2 or c in '\t', 'Unsafe one-byte glyph: '+repr(c))
                out += raw
            i += 1
        return bytes(out)

    def patched_pages(self):
        result = {}
        for mid, raw in self.pages.items():
            out = bytearray(raw)
            for code, im in self.glyphs.items():
                i=cell(code); x,y=(i%128)*32,(i//128)*32
                pixels=im.tobytes()
                for dy in range(32):
                    row=bytearray()
                    for v in pixels[dy*32:(dy+1)*32]:
                        n=v>>4; row += bytes((n*17,n*17))
                    p=128+((y+dy)*4096+x)*2
                    require(not any(raw[p:p+64]), 'Attempt to replace an occupied glyph')
                    out[p:p+64]=row
            result[mid]=bytes(out)
        return result


class Asm:
    def __init__(self):
        self.words=[]; self.labels={}; self.fixups=[]
    def emit(self,w): self.words.append(w)
    def label(self,k): self.labels[k]=len(self.words)
    def br(self,k,label):
        self.fixups.append((len(self.words),k,label)); self.emit(0)
    def code(self):
        forms={'b':0x48000000,'beq':0x41820000,'bne':0x40820000,
               'blt':0x41800000,'bge':0x40800000,'bgt':0x41810000}
        for i,k,label in self.fixups:
            d=(self.labels[label]-i)*4
            require(-32768<=d<32768,'Stub branch out of range')
            self.words[i]=forms[k]|(d & (0x3fffffc if k=='b' else 0xfffc))
        return b''.join(struct.pack('>I',w) for w in self.words)


def dform(op,t,a,v): return op|(t<<21)|(a<<16)|(v&65535)
def lis(t,v): return dform(0x3c000000,t,0,v)
def ori(a,t,v): return dform(0x60000000,t,a,v)
def addi(t,a,v): return dform(0x38000000,t,a,v)
def lwz(t,a,v): return dform(0x80000000,t,a,v)
def stw(t,a,v): return dform(0x90000000,t,a,v)
def lbz(t,a,v): return dform(0x88000000,t,a,v)
def lhz(t,a,v): return dform(0xa0000000,t,a,v)
def ld(t,a,v): return dform(0xe8000000,t,a,v&~3)
def std(t,a,v): return dform(0xf8000000,t,a,v&~3)
def cmpwi(a,v): return dform(0x2c000000,0,a,v)
def cmplw(a,b): return 0x7c000040|(a<<16)|(b<<11)
def mr(a,t): return 0x7c000378|(t<<21)|(a<<16)|(t<<11)
def add(t,a,b): return 0x7c000214|(t<<21)|(a<<16)|(b<<11)
def lwzx(t,a,b): return 0x7c00002e|(t<<21)|(a<<16)|(b<<11)
def lbzx(t,a,b): return 0x7c0000ae|(t<<21)|(a<<16)|(b<<11)
def lfs(t,a,v): return dform(0xc0000000,t,a,v)
def stfs(t,a,v): return dform(0xd0000000,t,a,v)
def fadds(t,a,b): return 0xec00002a|(t<<21)|(a<<16)|(b<<11)
def fmuls(t,a,c): return 0xec000032|(t<<21)|(a<<16)|(c<<6)
def branch(site,target,link=False):
    delta=target-site
    require(delta%4==0 and -0x2000000<=delta<0x2000000,'PPU branch range')
    return 0x48000000|(delta&0x3fffffc)|int(link)
def address(a,r,value):
    a.emit(lis(r,value>>16));a.emit(ori(r,r,value&65535))


def draw_stub(at, table):
    a=Asm(); save=(4,5,6,8,9,10)
    a.emit(dform(0xf8000001,1,1,-0x70))
    for i,r in enumerate(save): a.emit(std(r,1,0x20+i*8))
    a.emit(cmpwi(7,0));a.br('beq','done')
    a.emit(0x78000020|(3<<21)|(8<<16)) # clrldi r8,r3,32
    a.emit(lbz(0,8,0));a.emit(cmpwi(0,0));a.br('beq','done')
    a.emit(lbz(9,8,1));a.emit(dform(0x1c000000,0,0,256))
    a.emit(add(0,0,9));a.emit(dform(0x1c000000,0,0,4))
    address(a,11,table);a.emit(lwzx(11,11,0))
    a.emit(cmpwi(11,0));a.br('beq','done')
    a.label('entry');a.emit(lwz(12,11,0));a.emit(cmpwi(12,0));a.br('beq','done')
    a.emit(mr(5,8));a.emit(mr(6,12))
    a.label('compare');a.emit(lbz(9,5,0));a.emit(lbz(4,6,0))
    a.emit(cmplw(9,4));a.br('bne','next')
    a.emit(cmpwi(9,0));a.br('beq','found')
    a.emit(addi(5,5,1));a.emit(addi(6,6,1));a.br('b','compare')
    a.label('next');a.emit(addi(11,11,8));a.br('b','entry')
    a.label('found');a.emit(lwz(3,11,4))
    a.label('done')
    for i,r in enumerate(save):a.emit(ld(r,1,0x20+i*8))
    a.emit(addi(1,1,0x70));a.emit(0x2f870000)
    code=a.code();return code+struct.pack('>I',branch(at+len(code),DRAW+4))


def advance_stub(choice_cell=None):
    a=Asm();a.emit(lhz(0,1,0xc2))
    if choice_cell is not None:
        a.emit(cmpwi(0,choice_cell));a.br('beq','choice_tab')
    address(a,9,WIDTHS)
    a.emit(lbzx(0,9,0));a.emit(cmpwi(0,32));a.br('bne','letter')
    a.emit(lfs(13,1,0x94));a.br('b','acc')
    a.label('letter');a.emit(std(0,1,0xd0));a.emit(dform(0xc8000000,13,1,0xd0))
    a.emit(0xfc00069c|(13<<21)|(13<<11));a.emit(0xfc000018|(13<<21)|(13<<11))
    a.emit(lfs(10,1,0x9c));a.emit(fmuls(13,13,10))
    a.emit(lis(9,0x3d00));a.emit(stw(9,1,0xd0));a.emit(lfs(10,1,0xd0));a.emit(fmuls(13,13,10))
    if choice_cell is not None:
        a.br('b','acc')
        a.label('choice_tab')
        # NPJB00689 DRAW captures the line origin in f31 at 0x14180.
        # The loop keeps pen x at sp+0x84 and native pitch at sp+0x94.
        # Advance to origin + 3*pitch, independently of the glyph quad.
        a.emit(lfs(10,1,0x94));a.emit(fadds(13,10,10));a.emit(fadds(13,13,10))
        a.emit(fadds(13,31,13));a.emit(lfs(10,1,0x84))
        a.emit(0xec000028|(13<<21)|(13<<16)|(10<<11))  # fsubs f13,f13,f10
    a.label('acc');address(a,9,SCRATCH)
    a.emit(lfs(10,9,0));a.emit(fadds(10,10,13));a.emit(stfs(10,9,0));a.emit(0x4e800020)
    return a.code()


def keyword_position_stub():
    a=Asm()
    for w in (lbz(0,4,0x2f),0x7c000774,0x7c0001d6|(6<<11),
              lhz(11,4,0x22),0x7c000734|(11<<21)|(11<<16),
              add(11,11,0),stw(11,8,0),
              0x7c000670|(5<<21)|(7<<11),lhz(9,4,0x20),
              0x7c000734|(9<<21)|(9<<16),add(9,9,0),stw(9,7,0)):
        a.emit(w)
    address(a,10,SCRATCH);a.emit(addi(0,0,0));a.emit(stw(0,10,0));a.emit(0x4e800020)
    return a.code()


def keyword_acc_stub():
    a=Asm();address(a,10,SCRATCH);a.emit(lfs(13,10,0))
    a.emit(lis(0,0x4300));a.emit(stw(0,10,8));a.emit(lfs(12,10,8))
    a.emit(fmuls(13,13,12));a.emit(0xfc00001e|(13<<21)|(13<<11))
    a.emit(0x7c0007ae|(13<<21)|(10<<11));a.emit(lwz(9,10,0))
    a.emit(addi(0,0,0));a.emit(stw(0,10,0));a.emit(0x4e800020)
    return a.code()


def build_hook_table(pairs):
    buckets=defaultdict(list)
    for jp,en in sorted(pairs.items()):
        require(jp and b'\0' not in jp and b'\0' not in en,'NUL in hook text')
        key=(jp[0]<<8)|(jp[1] if len(jp)>1 else 0)
        buckets[key].append((jp,en))
    data=bytearray(65536*4); list_offsets={}
    for key,rows in sorted(buckets.items()):
        list_offsets[key]=len(data)
        struct.pack_into('>I',data,key*4,TEXT+len(data))
        data+=bytes((len(rows)+1)*8)
    pool={}
    def string(s):
        if s not in pool:
            pool[s]=TEXT+len(data);data.extend(s+b'\0')
        return pool[s]
    for key,rows in sorted(buckets.items()):
        for i,(jp,en) in enumerate(rows):
            j,e=string(jp),string(en)
            struct.pack_into('>II',data,list_offsets[key]+i*8,j,e)
    return bytes(data)


def patch_elf(original, codec, pairs, extra_edits=()):
    import rengoku_link_runtime as links
    import rengoku_combo_runtime as combo
    from rengoku_ui_runtime import (CENTER,CONVERTED,JOIN_TABLE,lookup_stub,
        converted_stub,center_stub,joined_stub,joined_data,draw_entry)
    require(sha(original)==ELF_SHA,'Wrong Rengoku ELF source')
    phoff=struct.unpack_from('>Q',original,32)[0]
    phsize,phnum=struct.unpack_from('>HH',original,54)
    require(phoff==64 and phsize==56 and phnum==8,'Unexpected program table')
    rows=[PH.unpack_from(original,phoff+i*56) for i in range(phnum)]
    require(rows[0][2:7]==(0,0x10000,0x10000,0x8eb408,0x8eb408),'Unexpected code LOAD')
    require(rows[1][2:7]==(0x8f0000,0x900000,0x900000,0x82384,0x3e8798),'Unexpected RW LOAD')
    require(all(r[3:7]==(0,0,0,0) for r in rows[2:5]),'Placeholder LOAD changed')
    require(original[DRAW-0x10000:DRAW-0x10000+12]==bytes.fromhex('2f8700007c0802a6f821fee1'),'Drawer prologue changed')
    require(struct.unpack_from('>I',original,ADVANCE-0x10000)[0]==0xc1a10094,'Advance site changed')
    require(original[0x4180:0x4184]==bytes.fromhex('ffe00890'),'Confirmation line origin changed')
    require(original[0x47d8:0x47ec]==bytes.fromhex('c0010084c1a10094ec00682ad00100844bfffa60'),
            'Confirmation pen/pitch loop changed')
    require(struct.unpack_from('>II',original,KW_ACC-0x10000)==(0x7c690e70,0x7d290194),'Keyword accumulator changed')
    require(original[UNICODE_TABLE+0x3041*2:UNICODE_TABLE+0x3045*2]==bytes.fromhex('829f82a082a182a2'),'Unicode table changed')
    for site in KW_CALLS:
        require(struct.unpack_from('>I',original,site-0x10000)[0]==branch(site,KW_POSITION,True),'Keyword caller changed')
    tail=rows[1][2]+rows[1][5]
    table=build_hook_table(pairs)
    end=align(TEXT+len(table),0x10000)
    # Preserve the alignment residue of every nonloaded section, including the
    # section-header table. Aligning the tail itself would shift all of them.
    tail_dest=end-0x10000+tail%16
    out=bytearray(original[:tail])+bytes(tail_dest-tail)+original[tail:]
    out[TEXT-0x10000:TEXT-0x10000+len(table)]=table
    edited=[]
    def put(off,data,label):
        out[off:off+len(data)]=data;edited.append({'offset':off,'bytes':len(data),'label':label})
    stubs={};cursor=CODE
    for name,make in [('lookup',lambda:lookup_stub(TEXT)),('joined',joined_stub),
                      ('draw',lambda:draw_entry(cursor,stubs['lookup'],stubs['joined'])),
                      ('advance',lambda:advance_stub(cell(codec.codes[CHOICE_PAD]) if CHOICE_PAD in codec.codes else None)),
                      ('keyword_position',keyword_position_stub),('keyword_acc',keyword_acc_stub)]:
        code=make();require(cursor+len(code)<=WIDTHS,'Stub overflow')
        stubs[name]=cursor;put(cursor-0x10000,code,name);cursor=align(cursor+len(code),16)
    for name,make in [('unicode_draw',lambda:converted_stub(cursor,stubs['lookup'])),
                      ('center',lambda:center_stub(cursor,stubs['lookup']))]:
        code=make();require(cursor+len(code)<=WIDTHS,'UI stub overflow')
        stubs[name]=cursor;put(cursor-0x10000,code,name);cursor=align(cursor+len(code),16)
    links.guard(original)
    for name,make in links.generators():
        code=make(cursor,stubs);require(cursor+len(code)<=WIDTHS,'Link stub overflow')
        stubs[name]=cursor;put(cursor-0x10000,code,name);cursor=align(cursor+len(code),16)
    for site,old,new,label in links.edits(stubs):
        require(struct.unpack_from('>I',original,site-0x10000)[0]==old,'Link instruction guard '+hex(site))
        put(site-0x10000,struct.pack('>I',new),label)
    combo.guard(original)
    code=combo.stub(cursor);require(cursor+len(code)<=WIDTHS,'Combo stub overflow')
    stubs['combo_scale']=cursor;put(cursor-0x10000,code,'Combo map scale')
    cursor=align(cursor+len(code),16)
    put(combo.SITE-0x10000,struct.pack('>I',branch(combo.SITE,stubs['combo_scale'])),
        'Combo popup uses map zoom once')
    require(original[CENTER-0x10000:CENTER-0x10000+16]==bytes.fromhex('f821ff417c0802a6fb610080836280c4'),'Rengoku centered drawer changed')
    require(original[CONVERTED-0x10000:CONVERTED-0x10000+12]==bytes.fromhex('83c280c43bfe00b84bfff7fc'),'Rengoku Unicode drawer changed')
    put(CENTER-0x10000,struct.pack('>I',branch(CENTER,stubs['center'])),'proportional centering')
    put(CONVERTED-0x10000,struct.pack('>I',branch(CONVERTED,stubs['unicode_draw'])),'Unicode draw translation')
    require(not any(original[CODE-0x10000:0x8f0000]),'Code gap is not empty')
    widths=bytearray([32]*FONT_CELLS)
    for i,w in codec.widths.items():widths[i]=w
    put(WIDTHS-0x10000,widths,'font widths')
    # Unit-test stand-ins do not implement the text codec.
    if hasattr(codec,'encode'):
        joined=joined_data(codec);require(JOIN_TABLE+len(joined)<0x900000,'Joined heading overflow')
        put(JOIN_TABLE-0x10000,joined,'joined Ace Bonus heading')
    put(DRAW-0x10000,struct.pack('>I',branch(DRAW,stubs['draw'])),'drawer entry')
    put(ADVANCE-0x10000,struct.pack('>I',branch(ADVANCE,stubs['advance'],True)),'glyph advance')
    put(KW_ACC-0x10000,struct.pack('>II',branch(KW_ACC,stubs['keyword_acc'],True),0x60000000),'keyword accumulator')
    for site in KW_CALLS:
        put(site-0x10000,struct.pack('>I',branch(site,stubs['keyword_position'],True)),'keyword position call')
    for ch,cp in codec.unicode.items():
        off=UNICODE_TABLE+cp*2
        require(struct.unpack_from('>H',original,off)[0]==0x81a1,'Private Unicode slot occupied')
        put(off,struct.pack('>H',codec.codes[ch]),'Unicode Latin mapping')
    for off,old,new,label in extra_edits:
        require(original[off:off+len(old)]==old and len(old)==len(new),'Extra ELF edit guard: '+label)
        put(off,new,label)
    # Keep exactly the native two LOADs. Materialize original BSS as zeros,
    # append owned text after BSS, and relocate only the nonloaded tail.
    newrows=list(rows)
    r=list(rows[0]);r[5]=r[6]=0x8f0000;newrows[0]=tuple(r)
    r=list(rows[1]);r[5]=r[6]=end-r[3];newrows[1]=tuple(r)
    delta=tail_dest-tail
    for i in range(2,5):
        r=list(rows[i]);r[2]+=delta;newrows[i]=tuple(r)
    for i,r in enumerate(newrows):PH.pack_into(out,phoff+i*56,*r)
    shoff=struct.unpack_from('>Q',original,40)[0];shsize,shnum=struct.unpack_from('>HH',original,58)
    require(shsize==64 and shoff>=tail,'Section table is not in the movable tail')
    struct.pack_into('>Q',out,40,shoff+delta)
    for i in range(shnum):
        before=SH.unpack_from(original,shoff+i*64);r=list(before)
        if r[1]!=8 and r[5] and not r[2]&2:
            require(r[4]>=tail and r[4]+r[5]<=len(original),'Unexpected nonloaded section extent')
            r[4]+=delta
        if r[8] and r[1]!=8:
            require(r[4]%r[8]==before[4]%r[8],'Section alignment changed')
        SH.pack_into(out,shoff+delta+i*64,*r)
    require((shoff+delta)%8==shoff%8,'Section-header table alignment changed')
    # Independently reconstruct original program bytes, allowing only listed edits.
    restored=bytearray(out[:tail])
    restored[40:48]=original[40:48]
    restored[phoff:phoff+56*phnum]=original[phoff:phoff+56*phnum]
    for e in edited:
        lo=e['offset'];hi=min(tail,lo+e['bytes'])
        if lo<tail:restored[lo:hi]=original[lo:hi]
    require(restored==original[:tail],'Unexpected change to original program bytes')
    require(not any(out[tail:TEXT-0x10000]),'Original BSS/scratch not zero-filled')
    require(out[TEXT-0x10000:TEXT-0x10000+len(table)]==table,'Runtime table changed')
    require(newrows[0][3]+newrows[0][6]<=newrows[1][3],'LOAD overlap')
    require(all(r[2]%r[7]==r[3]%r[7] and r[1]&3!=3 for r in newrows[:2]),'Invalid LOAD alignment/permissions')
    return bytes(out), {'source_sha256':ELF_SHA,'active_loads':2,'text_pairs':len(pairs),
                       'combo_popup':combo.report(),
                       'link_backgrounds':'measured dialogue/backlog geometry, speaker widths and scene/glossary identity',
                       'link_width_cache':links.LINK_WIDTHS,
                       'text_bytes':len(table),'font_glyphs':len(codec.codes),'stubs':stubs,
                       'edits':edited,'original_program_bytes_preserved_outside_edits':True,
                       'original_bss_zero_filled':True,'runtime_tested':False}
