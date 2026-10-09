"""Execute emitted PowerPC adapters; compare output, positions and ABI state."""
import importlib.util
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import rengoku_runtime as R
import rengoku_ui_runtime as U
import rengoku_screenshot_layout as L


def signed(x,n):return x-(1<<n) if x&(1<<(n-1)) else x
def f32(x):return struct.unpack('>f',struct.pack('>f',x))[0]


class Machine:
    def __init__(self,codec,pairs):
        self.mem={};self.r=[0x400000+i*256 for i in range(32)];self.r[1]=0x2000000;self.r[2]=0x3000000
        self.f=[struct.pack('>d',i+.125) for i in range(32)];self.cr=0xa53cc35a;self.lr=0x10000;self.codec=codec
        self.state=0x3100000;self.subject=0x3200000;self.put(self.state,bytes(0x2100))
        self.put(self.r[2]-0x7f3c,struct.pack('>I',self.state));self.put(self.r[1]-0x4000,bytes(0x4100))
        self.put(R.SCRATCH,bytes(256));self.put(R.TEXT,R.build_hook_table(pairs))
        self.put(R.WIDTHS,bytes(codec.widths.get(i,32) for i in range(R.FONT_CELLS)))
        self.put(U.JOIN_TABLE,U.joined_data(codec));self.stubs={};cursor=R.CODE
        for name,make in [('lookup',lambda:U.lookup_stub(R.TEXT)),('joined',U.joined_stub),
                         ('draw',lambda:U.draw_entry(cursor,self.stubs['lookup'],self.stubs['joined'])),
                         ('converted',lambda:U.converted_stub(cursor,self.stubs['lookup'])),
                         ('center',lambda:U.center_stub(cursor,self.stubs['lookup']))]:
            code=make();self.stubs[name]=cursor;self.put(cursor,code);cursor=R.align(cursor+len(code),16)
    def put(self,p,b):self.mem.update(enumerate(b,p))
    def get(self,p,n):return bytes(self.mem[p+i] for i in range(n))
    def cstr(self,p):
        out=bytearray()
        while self.mem[p]:out.append(self.mem[p]);p+=1
        return bytes(out)
    def rf(self,i):return struct.unpack('>d',self.f[i])[0]
    def wf(self,i,x):self.f[i]=struct.pack('>d',x)
    def style(self,quad,pitch,alternate=0,flags=()):
        for off,v in [(0x54,quad),(0x5c,pitch),(0x78,quad+3),(0x80,pitch+5),(0x88,quad+7),(0x90,pitch+11)]:
            self.put(self.state+off,struct.pack('>f',v))
        self.put(self.state+0xac,struct.pack('>H',alternate))
        for flag in flags:self.mem[self.state+flag]=1
    def run(self,name,text,mode=1,subject=None):
        p=self.subject if subject is None else subject
        if text is not None:self.put(p,text+b'\0'+bytes(32))
        self.r[3]=p;self.r[7]=mode;self.wf(1,640)
        self.initial=(self.r[:],self.f[:],self.cr,self.lr)
        pc=self.stubs[name];mask=(1<<64)-1
        for _ in range(100000):
            if pc in (R.DRAW,R.DRAW+4,U.CENTER+4,0x141a0):return pc
            if pc==U.CONVERT:
                text=self.cstr(self.r[3]).decode('utf-8')
                unicode_map={chr(u):self.codec.codes[c] for c,u in self.codec.unicode.items()}
                raw=b''.join(struct.pack('>H',unicode_map[c]) if c in unicode_map else c.encode('cp932') for c in text)
                self.put(self.state+0xb8,raw+b'\0')
                # Exercise the ABI: the real converter may clobber volatile regs.
                for i in range(3,13):self.r[i]=0x55550000+i
                for i in range(14):self.wf(i,i+100.25)
                self.cr=0x12345678;pc=self.lr;continue
            w=int.from_bytes(self.get(pc,4),'big');pc+=4
            op,t,a,b=w>>26,(w>>21)&31,(w>>16)&31,(w>>11)&31;imm=signed(w&65535,16);xo=(w>>1)&1023
            if op in (14,15):self.r[t]=((self.r[a] if a else 0)+imm*(65536 if op==15 else 1))&mask
            elif op==24:self.r[a]=self.r[t]|(w&65535)
            elif op==7:self.r[t]=(self.r[a]*imm)&mask
            elif op==31 and xo==266:self.r[t]=(self.r[a]+self.r[b])&mask
            elif op==31 and xo==444:self.r[a]=self.r[t]|self.r[b]
            elif op==31 and xo==19:self.r[t]=self.cr
            elif op==31 and xo==144:self.cr=self.r[t]&0xffffffff
            elif op==31 and xo==339:self.r[t]=self.lr
            elif op==31 and xo==467:self.lr=self.r[t]
            elif op in (32,34,40,58):
                n={32:4,34:1,40:2,58:8}[op];self.r[t]=int.from_bytes(self.get(self.r[a]+imm,n),'big')
            elif op==31 and xo in (23,87):
                self.r[t]=int.from_bytes(self.get(self.r[a]+self.r[b],4 if xo==23 else 1),'big')
            elif op in (10,11) or op==31 and xo==32:
                lhs=self.r[a]&0xffffffff;rhs=self.r[b]&0xffffffff if op==31 else w&65535
                if op==11:lhs=signed(lhs,32);rhs=imm
                shift=28-4*((w>>23)&7);self.cr=(self.cr&~(15<<shift))|((8 if lhs<rhs else 4 if lhs>rhs else 2)<<shift)
            elif op==18:
                if w&1:self.lr=pc
                pc=pc-4+signed(w&0x3fffffc,26)
            elif op==16:
                if bool(self.cr&(1<<(31-a)))==(t==12):pc=pc-4+signed(w&0xfffc,16)
            elif w==0x4e800020:pc=self.lr
            elif op in (36,62,54):
                off=signed(w&0xfffc,16) if op==62 else imm;addr=self.r[a]+off;n=4 if op==36 else 8
                value=self.f[t] if op==54 else (self.r[t]&mask).to_bytes(8,'big')
                self.put(addr,value[-n:])
                if op==62 and w&3==1:self.r[a]=addr
            elif op==48:self.wf(t,struct.unpack('>f',self.get(self.r[a]+imm,4))[0])
            elif op==50:self.f[t]=self.get(self.r[a]+imm,8)
            elif op==63 and xo==846:self.wf(t,float(signed(int.from_bytes(self.f[b],'big'),64)))
            elif op==63 and xo==12:self.wf(t,f32(self.rf(b)))
            elif op==59 and (w>>1)&31 in (20,21,25):
                kind=(w>>1)&31
                self.wf(t,f32(self.rf(a)-self.rf(b) if kind==20 else self.rf(a)+self.rf(b) if kind==21 else self.rf(a)*self.rf((w>>6)&31)))
            else:raise AssertionError('Unknown %08x at %x'%(w,pc-4))
        raise AssertionError('Adapter did not return')


class ScreenshotRuntime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not R.DEFAULT_FONT.exists():raise unittest.SkipTest('Local font unavailable')
        cls.codec=R.Codec([''.join(chr(c) for c in range(32,127))],{1:bytes(128+4096*1120*2),3:bytes(128+4096*1120*2)},R.DEFAULT_FONT)
    def machine(self):
        return Machine(self.codec,{'終了'.encode('cp932'):self.codec.encode('End Phase')})
    def test_center_modes_metrics_and_registers(self):
        for mode in (0,1):
            for alternate,flags in [(0,()),(1,()),(1,(0xae,0xaf,0xb1,0xb2))]:
                for text in ('End Phase','Battle Report','Quick Save','　End Phase'):
                    m=self.machine();m.style(28,42,alternate,flags)
                    raw=self.codec.encode(text,utf8=mode==0);dest=m.run('center',raw,mode)
                    self.assertEqual(dest,R.DRAW);self.assertEqual(m.cstr(m.r[3]),self.codec.encode(text));self.assertEqual(m.r[7],1)
                    expected=0
                    for c in text:
                        code=self.codec.codes[c] if c in self.codec.codes else int.from_bytes(c.encode('cp932'),'big')
                        off=0x54 if not alternate else 0x78
                        if alternate and any(lo<=code<=hi and flag in flags for flag,lo,hi in [(0xae,0x8260,0x8279),(0xaf,0x8281,0x829a),(0xb1,0x8340,0x8491),(0xb2,0x8140,0x825f)]):off=0x88
                        q=struct.unpack('>f',m.get(m.state+off,4))[0];pitch=struct.unpack('>f',m.get(m.state+off+8,4))[0]
                        w=self.codec.widths.get(R.cell(code),32);expected+=pitch if w==32 else q*w/32
                    self.assertAlmostEqual(m.rf(1),640-expected/2,places=4)
                    ri,fi,cr,lr=m.initial
                    self.assertTrue(all(m.r[i]==ri[i] for i in range(32) if i not in (3,7)))
                    self.assertTrue(all(m.f[i]==fi[i] for i in range(32) if i!=1));self.assertEqual(m.cr,cr);self.assertEqual(m.lr,lr)
    def test_center_translation_and_fallback(self):
        for mode in (0,1):
            m=self.machine();m.style(28,42)
            self.assertEqual(m.run('center','終了'.encode('utf-8' if not mode else 'cp932'),mode),R.DRAW)
            self.assertEqual(m.cstr(m.r[3]),self.codec.encode('End Phase'))
        for text in ('未知'.encode('cp932'),b'ASCII',b'\x81',b'\n'):
            m=self.machine();m.style(28,42);self.assertEqual(m.run('center',text),U.CENTER+4)
            ri,fi,cr,lr=m.initial;self.assertEqual(m.r[3:],ri[3:]);self.assertEqual(m.f,fi);self.assertEqual(m.cr,cr);self.assertEqual(m.lr,lr)
            self.assertEqual(m.r[1],ri[1]-0xc0)
    def test_converted_unicode_path_translates(self):
        m=self.machine();m.put(m.state+0xb8,'終了'.encode('cp932')+b'\0')
        self.assertEqual(m.run('converted',b'ignored'),0x141a0)
        self.assertEqual(m.cstr(m.r[31]),self.codec.encode('End Phase'))
    def test_joined_heading_suppresses_only_its_remaining_parts(self):
        for raw in ('エースボーナス'.encode('cp932'),self.codec.encode('Ace Bonus')):
            pieces=[raw[i:i+4] for i in range(0,len(raw),4)];split=b'\0\0'.join(pieces)
            m=self.machine();self.assertEqual(m.run('draw',split),R.DRAW+4)
            self.assertEqual(m.cstr(m.r[3]),self.codec.encode('Ace Bonus'))
            self.assertEqual(m.run('draw',None,subject=m.subject+len(pieces[0])+2),R.DRAW+4)
            self.assertEqual(m.cstr(m.r[3]),b'')
            m.run('draw',self.codec.encode('Different'));self.assertEqual(m.cstr(m.r[3]),self.codec.encode('Different'))
    def test_compact_slots_and_skill_levels(self):
        messages={str(i):{'source':jp,'text':en} for i,(jp,en) in enumerate([('底力','Potential'),('援護攻撃','Support Atk'),('援護防御','Support Def')])}
        hooks=L.hooks(self.codec,messages)
        self.assertEqual(hooks['援護攻撃Ｌ２'.encode('cp932')],self.codec.encode('Support Atk L2'))
        self.assertEqual(len(self.codec.encode(L.text_for_field('空陸海宇','Air Land Sea Space'))),8)
        for c in R.COMPACT_LABELS:self.assertEqual(self.codec.widths[R.cell(self.codec.codes[c])],32)


if __name__=='__main__':unittest.main()
