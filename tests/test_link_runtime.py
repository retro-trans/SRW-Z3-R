"""Execute Rengoku's native link/name consumers with the emitted PPC patches.

Only allocator/scene/style/CRT calls have fixtures. The real record getter,
registration loop, glyph advance, name rectangle tail and patch code execute.
External call fixtures destroy volatile registers to catch live-state mistakes.
"""
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import rengoku_runtime as R
import rengoku_link_runtime as L

ROOT=Path(__file__).resolve().parents[1]


def signed(x,n):
    x&=(1<<n)-1
    return x-(1<<n) if x>>(n-1) else x


class CPU:
    def __init__(self,blob):
        self.regions=[]
        phoff=struct.unpack_from('>Q',blob,32)[0]
        for i in range(struct.unpack_from('>H',blob,56)[0]):
            kind,flags,off,va,pa,size,memsz,align=R.PH.unpack_from(blob,phoff+i*56)
            if kind==1 and size:self.regions.append((va,memoryview(blob)[off:off+size]))
        self.mem={};self.r=[0x2800000+i*0x1000 for i in range(32)]
        self.f=[i+.25 for i in range(32)];self.cr=[0]*8;self.lr=0x10000
        self.calls={};self.writes=set();self.carry=0
        self.r[1]=0x2000000;self.r[2]=0x2900000
        self.put(self.r[1]-0x4000,bytes(0x4400));self.writes.clear()
    def read(self,p,n):
        def byte(p):
            if p in self.mem:return self.mem[p]
            for base,raw in self.regions:
                if base<=p<base+len(raw):return raw[p-base]
            raise AssertionError('Unmapped read '+hex(p))
        return bytes(byte(p+i) for i in range(n))
    def put(self,p,raw):
        self.mem.update(enumerate(raw,p));self.writes.update(range(p,p+len(raw)))
    def u32(self,p):return int.from_bytes(self.read(p,4),'big')
    def string(self,p):
        raw=bytearray()
        while self.read(p,1)!=b'\0':raw+=self.read(p,1);p+=1
        return bytes(raw)
    def run(self,pc,ends):
        r,f=self.r,self.f
        for _ in range(200000):
            if pc in ends:return pc
            if pc in self.calls:
                result=self.calls[pc](self)
                for j in [0]+list(range(3,13)):r[j]=0xbad00000+j
                f[:14]=[12345.]*14;self.cr=[99]*8;r[3]=result;pc=self.lr;continue
            w=self.u32(pc);op,t,a,b=w>>26,(w>>21)&31,(w>>16)&31,(w>>11)&31
            imm=signed(w,16);following=pc+4;xo=(w>>1)&1023
            if op==18:
                following=pc+signed(w&0x3fffffc,26)
                if w&1:self.lr=pc+4
            elif op==16:
                bo,bi=t,a;cmp=self.cr[bi//4]
                assert bo in (4,12) and bi%4<3
                if (cmp<0,cmp>0,cmp==0)[bi%4]==(bo==12):following=pc+signed(w&0xfffc,16)
            elif w==0x4e800020:following=self.lr
            elif op==14:r[t]=(r[a] if a else 0)+imm
            elif op==15:r[t]=(r[a] if a else 0)+(imm<<16)
            elif op==24:r[a]=r[t]|(w&65535)
            elif op==7:r[t]=r[a]*imm
            elif op in (10,11):self.cr[(w>>23)&7]=(r[a]&0xffffffff)-(w&65535) if op==10 else signed(r[a],32)-imm
            elif op==21:
                sh,mb,me=(w>>11)&31,(w>>6)&31,(w>>1)&31
                assert mb<=me
                val=r[t]&0xffffffff;rot=((val<<sh)|(val>>(32-sh if sh else 32)))&0xffffffff
                r[a]=rot&sum(1<<(31-i) for i in range(mb,me+1))
            elif op==30:
                mb=((w>>6)&31)|(w&32);assert (w&0x1c)==0
                r[a]=r[t]&((1<<(64-mb))-1)
            elif op in (32,34,40,58):
                n={32:4,34:1,40:2,58:8}[op]
                r[t]=int.from_bytes(self.read((r[a] if a else 0)+imm,n),'big')
            elif op==31:
                if xo in (0,32):self.cr[(w>>23)&7]=(signed(r[a],32)-signed(r[b],32) if xo==0 else (r[a]&0xffffffff)-(r[b]&0xffffffff))
                elif xo==444:r[a]=r[t]|r[b]
                elif xo==266:r[t]=r[a]+r[b]
                elif xo==40:r[t]=r[b]-r[a]
                elif xo==235:r[t]=signed(r[a],32)*signed(r[b],32)
                elif xo in (23,87):r[t]=int.from_bytes(self.read((r[a] if a else 0)+r[b],4 if xo==23 else 1),'big')
                elif xo in (922,954,986):r[a]=signed(r[t],{922:16,954:8,986:32}[xo])
                elif xo==824:
                    value=signed(r[t],32);r[a]=value>>b
                    self.carry=int(value<0 and bool(value&((1<<b)-1)))
                elif xo==202:r[t]=r[a]+self.carry
                elif xo==19:
                    r[t]=sum((8 if c<0 else 4 if c>0 else 2)<<(28-i*4) for i,c in enumerate(self.cr))
                elif xo==144:
                    self.cr=[-1 if r[t]&(8<<(28-i*4)) else 1 if r[t]&(4<<(28-i*4)) else 0 for i in range(8)]
                elif w==0x7c0802a6:r[0]=self.lr
                elif w==0x7c0803a6:self.lr=r[0]
                else:raise AssertionError((hex(pc),hex(w)))
            elif op in (48,50):
                raw=self.read(r[a]+imm,4 if op==48 else 8)
                f[t]=struct.unpack('>f',raw)[0] if op==48 else raw
            elif op==63:
                if xo==846:f[t]=float(int.from_bytes(f[b],'big',signed=True))
                elif xo==12:f[t]=struct.unpack('>f',struct.pack('>f',f[b]))[0]
                else:raise AssertionError((hex(pc),hex(w)))
            elif op==59:
                kind=(w>>1)&31
                if kind==20:f[t]=f[a]-f[b]
                elif kind==21:f[t]=f[a]+f[b]
                elif kind==25:f[t]=f[a]*f[(w>>6)&31]
                else:raise AssertionError((hex(pc),hex(w)))
                f[t]=struct.unpack('>f',struct.pack('>f',f[t]))[0]
            elif op in (36,38,44,52,62):
                n={36:4,38:1,44:2,52:4,62:8}[op]
                address=(r[a] if a else 0)+(signed(w&0xfffc,16) if op==62 else imm)
                raw=struct.pack('>f',f[t]) if op==52 else (r[t]&((1<<(8*n))-1)).to_bytes(n,'big')
                self.put(address,raw)
                if op==62 and w&3==1:r[a]=address
            else:raise AssertionError((hex(pc),hex(w)))
            pc=following
        raise AssertionError('Unbounded execution')


class LinkRuntime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=ROOT/'work/eboot/EBOOT.ELF'
        if not source.exists() or not R.DEFAULT_FONT.exists():raise unittest.SkipTest('Local game/font unavailable')
        cls.source=source.read_bytes()
        cls.codec=R.Codec([''.join(chr(c) for c in range(32,127))],
            {1:bytes(128+4096*1120*2),3:bytes(128+4096*1120*2)},R.DEFAULT_FONT)
        cls.pairs={jp.encode('cp932'):cls.codec.encode(en) for jp,en in
            [('ブルー','Blue'),('エルガン','Elgan'),('改革派','Reformists')]}
        cls.new,cls.report=R.patch_elf(cls.source,cls.codec,cls.pairs)
        old=bytearray(cls.new)
        for site,original,_,_ in L.edits(cls.report['stubs']):struct.pack_into('>I',old,site-0x10000,original)
        cls.old=bytes(old);cls.stubs=cls.report['stubs']
    def cpu(self,legacy=False):
        c=CPU(self.old if legacy else self.new)
        c.calls[L.STRLEN]=lambda cpu:len(cpu.string(cpu.r[3]))
        c.calls[L.STRCMP]=lambda cpu:int(cpu.string(cpu.r[3])!=cpu.string(cpu.r[4]))
        return c
    def primary(self,c,slot=17,selected=1,scene=0x2300000,x=700,y=600,width=173.25):
        manager,records,style,widget,ctx,rect=0x2100000,0x2110000,0x2120000,0x2130000,0x2130100,0x2140000
        c.put(manager,bytes(0x48));c.put(records,bytes(256*20))
        for bank in range(16):c.put(manager+4+bank*4,struct.pack('>I',records+bank*320))
        c.put(0x2150000,bytes(12)+struct.pack('>I',scene))
        c.put(widget+4,struct.pack('>I',widget+0x80));c.put(widget+0x80,bytes([0,0,0,selected]))
        c.put(style,bytes(0x40));c.put(style+0x2d,bytes([31]))
        c.put(rect,bytes(32));c.put(L.LINK_WIDTHS+slot*4,struct.pack('>f',width))
        record=struct.pack('>hhBBBBIII',x,y,222,1,31,35,0xabcdef,scene,selected)
        c.put(records+slot*20,record)
        c.r[28]=ctx;c.r[31]=widget;c.r[30]=rect
        def get_style(cpu):
            self.assertEqual((cpu.r[3],cpu.r[4]),(widget,ctx))
            return style
        c.calls[L.SCENE_MANAGER]=lambda cpu:0x2150000
        c.calls[L.LINK_MANAGER]=lambda cpu:manager
        c.calls[L.GET_STYLE]=get_style
        return records+slot*20,record,rect
    def test_primary_all_slots_uses_rendered_geometry_and_keeps_context(self):
        for slot in range(256):
            c=self.cpu();record,before,rect=self.primary(c,slot,x=-15,y=-7,width=slot+.375)
            initial=c.r[:];c.writes.clear();c.run(L.PRIMARY,{L.PRIMARY_TAIL})
            self.assertEqual(struct.unpack('>4f',c.read(rect,16)),(-15.,-6.,slot+.375,32.))
            self.assertEqual(c.read(record,20),before)
            self.assertTrue(all(c.r[i]==initial[i] for i in [1,2]+list(range(13,27))+[28,30,31]))
            allowed=set(range(initial[1]+0x70,initial[1]+0x80))|set(range(initial[1]+0xa0,initial[1]+0xa8))|set(range(rect,rect+16))
            self.assertTrue(c.writes<=allowed)
    def test_primary_rejects_stale_scene_wrong_identity_inactive_and_null_scene(self):
        for off,raw in [(12,struct.pack('>I',99)),(16,struct.pack('>I',7)),(5,b'\0')]:
            c=self.cpu();record,before,rect=self.primary(c);c.put(record+off,raw)
            c.run(L.PRIMARY,{L.PRIMARY_TAIL});self.assertEqual(c.read(rect,16),bytes(16))
        c=self.cpu();_,_,rect=self.primary(c,scene=0)
        c.run(L.PRIMARY,{L.PRIMARY_TAIL});self.assertEqual(c.read(rect,16),bytes(16))
    def test_original_primary_reproduces_offscreen_background(self):
        c=self.cpu(True);_,_,rect=self.primary(c,x=678,y=560,width=145.25)
        style=0x2120000;c.r[3]=style
        c.put(style+0x20,struct.pack('>hh',232,560));c.put(style+0x2d,bytes([31,31,35]))
        # An English link after column 34 was placed past the 1280px viewport.
        c.put(c.r[1]+0x70,bytes([0,34,10]))
        c.run(0x21228c,{L.PRIMARY_TAIL})
        self.assertEqual(struct.unpack('>4f',c.read(rect,16)),(1286.,561.,310.,32.))
        c=self.cpu();_,_,rect=self.primary(c,x=678,y=560,width=145.25)
        c.run(L.PRIMARY,{L.PRIMARY_TAIL})
        self.assertEqual(struct.unpack('>4f',c.read(rect,16)),(678.,561.,145.25,32.))
    def test_secondary_every_slot_width_and_reuse_without_record_changes(self):
        c=self.cpu();record=0x2200000;rect=0x2201000
        for slot in range(256):
            c.r[28]=record;c.r[3]=18;c.put(record,bytes(range(20)))
            c.put(c.r[1]+0x70,struct.pack('>II',slot//16,slot%16))
            c.put(R.SCRATCH,struct.pack('>f',slot+.375));c.lr=0x10000
            c.run(self.stubs['link_capture'],{0x10000})
            self.assertEqual(c.read(record,20),bytes(range(4))+b'\x12'+bytes(range(5,20)))
            self.assertEqual(c.read(R.SCRATCH,4),struct.pack('>f',slot+.375))
        for slot in (0,1,15,16,127,255,-1,256):
            c.r[4]=slot;c.r[3]=record;c.lr=0x10000;cr=c.cr[:]
            c.run(self.stubs['link_select'],{0x10000});self.assertEqual(c.cr,cr)
            c.r[31]=rect;c.put(rect,bytes(range(24)));c.f[0]=999.;c.lr=0x10000
            c.run(self.stubs['link_width'],{0x10000})
            self.assertEqual(c.read(rect,24),bytes(range(8))+struct.pack('>f',(slot&255)+.375)+bytes(range(12,24)))
        c.r[28]=record;c.r[3]=18;c.put(c.r[1]+0x70,bytes(8));c.put(R.SCRATCH,struct.pack('>f',44.5));c.lr=0x10000
        c.run(self.stubs['link_capture'],{0x10000});self.assertEqual(c.read(L.LINK_WIDTHS,4),struct.pack('>f',44.5))
    def test_capture_uses_actual_glyph_advances(self):
        for text in ('Blue','Elgan','Reformists','Wiii','日本'):
            raw=self.codec.encode(text)
            for quad,pitch in ((24,31),(28,42),(32,32)):
                c=self.cpu();c.put(R.SCRATCH,bytes(4));expected=0.
                for start in range(0,len(raw),2):
                    cell=R.cell(int.from_bytes(raw[start:start+2],'big'))
                    c.put(c.r[1]+0xc2,struct.pack('>H',cell))
                    c.put(c.r[1]+0x94,struct.pack('>f',pitch));c.put(c.r[1]+0x9c,struct.pack('>f',quad))
                    c.lr=0x10000;c.run(self.stubs['advance'],{0x10000})
                    width=self.codec.widths.get(cell,32)
                    expected+=pitch if width==32 else quad*width/32
                c.r[28]=0x2200000;c.r[3]=len(raw);c.put(c.r[1]+0x70,bytes(8));c.lr=0x10000
                c.run(self.stubs['link_capture'],{0x10000})
                self.assertEqual(struct.unpack('>f',c.read(L.LINK_WIDTHS,4))[0],expected)
    def name(self,raw,quad,pitch,legacy=False):
        c=self.cpu(legacy);widget,rect,pointer=0x2200000,0x2201000,0x2202000
        c.put(pointer,raw+b'\0');c.put(widget,bytes(0x68));c.put(rect,bytes(24))
        c.put(widget+4,struct.pack('>ffIIII',215.,416.,quad,quad,pitch,29))
        c.put(c.r[2]-0x23c4,struct.pack('>f',1.));c.r[3]=pointer;c.r[31]=widget;c.r[29]=rect
        before=c.read(widget,0x68);c.run(L.NAME_SITE,{0x2a72ac})
        self.assertEqual(c.read(widget,0x68),before)
        self.assertEqual(struct.unpack('>ff',c.read(rect+12,8)),(445.,1.))
        return struct.unpack('>f',c.read(rect+8,4))[0]-215
    def test_native_speaker_name_widget_blue_and_fallback(self):
        for name in ('Blue','Elgan','Advent','Wiii'):
            raw=self.codec.encode(name)
            for quad,pitch in ((24,31),(21,27),(32,42)):
                expected=sum(self.codec.widths[R.cell(self.codec.codes[ch])] for ch in name)*quad/32
                self.assertEqual(self.name(raw,quad,pitch),expected)
                self.assertEqual(self.name(raw,quad,pitch,True),len(name)*pitch)
                if name=='Blue':self.assertEqual(self.name('ブルー'.encode('cp932'),quad,pitch),expected)
        for raw in ('日本'.encode('cp932'),b'Custom',b'',b'\xff\xff'):
            self.assertEqual(self.name(raw,24,31),len(raw)//2*31)
    def test_native_registration_scene_and_translated_glossary_feed_primary(self):
        for explicit,current in ((0,0x2300000),(0x2301000,0x2300000),(0,0)):
            for selected in (0,1):
                for legacy in (False,True):
                    c=self.cpu(legacy);scene=explicit or current;ctx=0x2310000;record=0x2320000
                    c.put(ctx,bytes(4)+struct.pack('>I',explicit));c.put(record,bytes(20))
                    c.put(0x2310100,bytes(12)+struct.pack('>I',current))
                    c.calls[L.SCENE_MANAGER]=lambda cpu:0x2310100
                    keys=['エルガン','改革派'];terms=[self.pairs[k.encode('cp932')] for k in keys]
                    for index,key in enumerate(keys):
                        c.put(0x2330000+index*0x100,key.encode('cp932')+b'\0')
                        c.put(0x2331000+index*4,struct.pack('>I',0x2330000+index*0x100))
                    if scene:
                        c.put(scene+0x18,struct.pack('>I',0x2340000))
                        c.put(0x2340000,struct.pack('>II',0x2341000,2));c.put(0x2341000,struct.pack('>II',10,11))
                    c.calls[0x21a388]=lambda cpu:0x2331000+(cpu.r[3]-10)*4
                    c.put(0x2350000,terms[selected]+b'\0')
                    c.r[3]=ctx;c.r[28]=record;c.r[30]=0;c.r[27]=0x2350000
                    c.run(L.SCENE_SITE,{0x21a584,0x21a5f8})
                    assigned=struct.unpack('>II',c.read(record+12,8))
                    self.assertEqual(assigned,((explicit,0) if legacy else (scene,selected if scene else 0)))
                    if scene and not legacy:
                        registered=c.read(record+12,8);rec,_,rect=self.primary(c,selected=selected,scene=scene)
                        c.put(rec+12,registered);c.run(L.PRIMARY,{L.PRIMARY_TAIL})
                        self.assertEqual(struct.unpack('>4f',c.read(rect,16)),(700.,601.,173.25,32.))
    def test_source_guards_and_no_sibling_addresses(self):
        L.guard(self.source)
        for site,_,_,_ in L.edits(self.stubs):
            broken=bytearray(self.source);broken[site-0x10000]^=1
            with self.assertRaises(ValueError):L.guard(broken)
        required={'lookup','joined','draw','advance','keyword_position',
                  'keyword_acc','unicode_draw','center'}|{name for name,_ in L.generators()}
        self.assertLessEqual(required,set(self.report['stubs']))
        self.assertLess(self.stubs['link_name']+len(L.name_stub(self.stubs['link_name'],self.stubs['lookup'])),R.WIDTHS)


if __name__=='__main__':unittest.main()
