"""Rengoku SR reward variants: one notification and a separate amount field."""
import struct
from rengoku_runtime import require
from rengoku_search_layout import field
from rengoku_screenshot_layout import line_width

def apply_fssa(source,built,codec):
 out=bytearray(built);base=struct.unpack_from('>I',source,32)[0];allowed=set();report=[]
 for p in (0x8bfe4,0x99d84):
  require(field(source,p)=='ＳＲポイント'.encode('cp932'),'SR placeholder source changed')
  dest=len(out);out+=b'\0';struct.pack_into('>I',out,p,dest-base);allowed.update(range(p,p+4))
  report.append({'row':hex(p),'display':'','reason':'redundant colored placeholder behind complete notification'})
 p,n=0x99da4,0x99dc4
 require(field(source,p)=='ボーナス資金１００００を入手しました。'.encode('cp932'),'Reward sentence changed')
 require(field(source,n)=='１００００'.encode('cp932'),'Reward amount source changed')
 require(source[p+16:p+24]==bytes.fromhex('1f1f1b1f1f1f0040') and source[n+16:n+24]==bytes.fromhex('1f1f1b1f1f1f3040'),'Reward styles changed')
 label='Bonus funds received:';pw=line_width(codec,label,31)
 # Native fullwidth digits stay in their original amount field. Measure the
 # actual preserved string rather than an ASCII spelling with narrower ink.
 nw=line_width(codec,field(built,n).decode('cp932'),31);gap=18
 left=639.5-(pw+gap+nw)/2
 dest=len(out);out+=codec.encode(label)+b'\0';struct.pack_into('>I',out,p,dest-base);allowed.update(range(p,p+4))
 for row,x in ((p,left),(n,left+pw+gap)):
  struct.pack_into('>f',out,row+4,(x-640)/640);out[row+23]&=~0x40
  allowed.update(range(row+4,row+8));allowed.add(row+23)
 require(out[n:n+4]==built[n:n+4],'Live amount pointer changed')
 require(all(a==b or i in allowed for i,(a,b) in enumerate(zip(built,out))),'Unexpected SR reward change')
 report.append({'row':hex(p),'display':label,'label_x':left,'label_width':pw,'amount_x':left+pw+gap,'amount_width':nw,'gap':gap,'amount_field_preserved':True})
 return bytes(out),report
