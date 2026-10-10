"""Paint shared Center/Wide/Attack word cells; preserve native quads/tint/timing."""
import struct
from PIL import Image,ImageDraw,ImageFont
from rengoku_runtime import require,sha,DEFAULT_FONT
from rengoku_intermission_layout import morton,ART_SHA
RECTS=((160,0,136,40,'Center',0x4a408),(296,0,96,40,'Wide',0x4a4d0),(80,0,80,40,'Attack',0x4a46c))
def tile(w,h,label,font):
 face=ImageFont.truetype(str(font),120);l,t,r,b=face.getbbox(label)
 mask=Image.new('RGBA',(r-l,b-t));ImageDraw.Draw(mask).text((-l,-t),label,font=face,fill='white')
 mask=mask.resize((min(w-8,round(mask.width/4)),28),Image.Resampling.LANCZOS)
 result=Image.new('RGBA',(w,h));result.alpha_composite(mask,((w-mask.width)//2,3));return result
def apply(source,built,fssa,font=DEFAULT_FONT):
 require(sha(source)==ART_SHA,'Attack word atlas source changed')
 p=12+36*2;require(source[p+12]==0x85 and struct.unpack_from('>HH',source,p+20)==(512,512),'Attack atlas layout')
 start=struct.unpack_from('>I',source,p+4)[0];out=bytearray(built);allowed=set()
 for x,y,w,h,label,q in RECTS:
  expected=((x+w/2)/512,(y+h/2)/512),(x/512,y/512),((x+w)/512,y/512),((x+w)/512,(y+h)/512),(x/512,(y+h)/512)
  require(tuple(struct.unpack_from('>2f',fssa,q+i*20+12) for i in range(5))==expected,'Attack UV source changed')
  im=tile(w,h,label,font)
  for yy in range(h):
   for xx in range(w):
    r,g,b,a=im.getpixel((xx,yy));at=start+morton(x+xx,y+yy)*4
    out[at:at+4]=bytes((a,r,g,b));allowed.update(range(at,at+4))
 require(all(a==b or i in allowed for i,(a,b) in enumerate(zip(built,out))),'Unexpected attack artwork mutation')
 return bytes(out)
