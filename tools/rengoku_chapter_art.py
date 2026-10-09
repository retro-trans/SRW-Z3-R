"""Rengoku chapter titles and animated episode headers; no source writes.

CLI previews are dry-run by default. --write requires a fresh work/ directory.
Uses the existing canonical artwork English and PS3 Seurat face. Geometry was
located in Rengoku EFF members 100/101; its mode words end in 01, unlike Z3.1.
"""
import argparse
import json
import struct
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from cpk import CPK
from inspect_artwork import textures
from rengoku_runtime import require,sha,DEFAULT_FONT

ROOT=Path(__file__).resolve().parents[1]
TPACK='USRDIR/DATA_REN/TABATA/TPACKPS3.CPK'
EFF='USRDIR/DATA_REN/ANIME/EFFPS3.CPK'
EFFECTS={100:(0xdf450,'9024998abbaea3353da34454994aafd7608b33414a105173b39cb1c8bcb1fef9'),
         101:(0x101c70,'325b5201a252e264dc2f8ab60fcacf76f6e1d941185217c0d7993f4d05277430'),
         102:(0xc5ef0,'929680deda0cea3514bd4706967efd7ae87c53a3f0eae6909bb3c6468681d909')}


def catalog():
    path=ROOT/'source/artwork.json';raw=path.read_bytes();src=json.loads(raw)
    loc=json.loads((ROOT/'localization/locales/en/artwork.json').read_text(encoding='utf8'))
    require(loc['source_catalog_sha256']==sha(raw),'Artwork source catalog changed')
    result={}
    for row in src['records']:
        if row['region']!='chapter title, normal and glow copies':continue
        v=loc['messages'][row['id']]
        require(v['source']==row['source'] and v['source_sha256']==sha(row['source'].encode()),'Chapter source binding')
        require(v['text'] and '$$' not in v['text'],'Unresolved chapter title')
        mid=int(row['asset'].rsplit(':',1)[1]);result[mid]=dict(row,english=v['text'])
    require(set(result)==set(range(4,19)),'Expected all 15 Rengoku cards')
    return result


def word(text,font,size,bounds):
    face=ImageFont.truetype(str(Path(font).with_name('SCE-PS3-SR-R-LATIN.TTF')),size*2)
    l,t,r,b=face.getbbox(text);ink=Image.new('RGBA',(r-l,b-t))
    ImageDraw.Draw(ink).text((-l,-t),text,font=face,fill='white')
    scale=min(.5,bounds[0]/ink.width,bounds[1]/ink.height)
    return ink.resize((round(ink.width*scale),round(ink.height*scale)),Image.Resampling.LANCZOS)


def glow(im):
    out=im.filter(ImageFilter.GaussianBlur(3));out.alpha_composite(im);return out


def argb(im):
    r,g,b,a=im.split();return Image.merge('RGBA',(a,r,g,b)).tobytes()


def title_image(text,font):
    tile=Image.new('RGBA',(1536,128));ink=word(text,font,140,(1280,104))
    tile.alpha_composite(ink,((1536-ink.width)//2,(128-ink.height)//2))
    page=Image.new('RGBA',(1536,256));page.paste(tile,(0,0));page.paste(glow(tile),(0,128))
    return page


def title_apply(raw,row,font):
    require(sha(raw)==row['asset_sha256'],'Chapter source image changed')
    require(raw[24]==0xa5 and struct.unpack_from('>HH',raw,32)==(1536,256),'Chapter GTF layout')
    off,n=struct.unpack_from('>II',raw,16);require(n==1536*256*4,'Chapter pixel length')
    return raw[:off]+argb(title_image(row['english'],font))+raw[off+n:]


def geometry(raw,member):
    gtf,_=EFFECTS[member];edits=[];counts=[0,0,0]
    for p in range(40,gtf-16,2):
        z,x,y,w,h,flags,mode,tex=struct.unpack_from('>8H',raw,p)
        if z or flags!=0x5000 or mode not in (0x0101,0x0201):continue
        coords=list(struct.unpack_from('>8h',raw,p-16))
        if tex==2 and y==0 and w==144 and h==112 and x in (0,288):
            require(coords in ([-338,-145,-274,-145,-338,-95,-274,-95],
                              [-337,-145,-273,-145,-337,-95,-273,-95]),'Episode header quad')
            coords[2]+=128;coords[6]+=128
            edits.extend([(p-16,struct.pack('>8h',*coords)),(p+6,struct.pack('>H',288))]);counts[0]+=1
        elif tex in ((4,) if member==100 else (4,5)) and x==0 and y in (0,112) and w==96 and h==112:
            expected=([-275,-150,-223,-150,-275,-90,-223,-90] if member==100 else
                      ([-230,-150,-178,-150,-230,-90,-178,-90] if tex==4 else
                       [-277,-150,-225,-150,-277,-90,-225,-90]))
            require(coords==expected,'Episode digit quad')
            for i in (0,2,4,6):coords[i]+=128
            edits.append((p-16,struct.pack('>8h',*coords)));counts[1]+=1
        elif tex==2 and y==0 and w==144 and h==112 and x in (144,432):
            # Remove 話 via vertex colors, keeping adjacent logo pixels intact.
            edits.append((p-40,bytes(16)));counts[2]+=1
    require(counts==[1691,1674 if member==100 else 3348,1650],'Episode animation coverage: '+repr(counts))
    return edits,counts


def paint(out,gtf,tex,rect,im):
    x,y,w,h=rect;p=gtf+12+36*tex;tw,th=struct.unpack_from('>HH',out,p+20)
    require(out[p+12]==0xa5 and im.size==(w,h) and x+w<=tw and y+h<=th,'Episode atlas rectangle')
    base=gtf+struct.unpack_from('>I',out,p+4)[0];data=argb(im)
    for row in range(h):
        q=base+((y+row)*tw+x)*4;out[q:q+w*4]=data[row*w*4:(row+1)*w*4]


def effect_apply(raw,member,font,fallback):
    gtf,fingerprint=EFFECTS[member]
    require(sha(raw)==fingerprint and raw[gtf:gtf+4]==b'\x02\x02\0\0','Rengoku episode effect source')
    out=bytearray(raw)
    # All three atlases carry the same final header. Member 102 draws its
    # final title from this atlas too, unlike the two numbered animations.
    tile=Image.new('RGBA',(432,112));ink=word('Final Episode',font,140,(408,88))
    tile.alpha_composite(ink,((432-ink.width)//2,(112-ink.height)//2))
    for y,im in ((0,tile),(112,glow(tile))):paint(out,gtf,2,(592,y,432,112),im)
    if member==102:
        tile=Image.new('RGBA',(1024,128));ink=word(fallback,font,140,(1000,104))
        tile.alpha_composite(ink,((1024-ink.width)//2,(128-ink.height)//2))
        for y,im in ((544,tile),(672,glow(tile))):paint(out,gtf,2,(0,y,1024,128),im)
        off=gtf+struct.unpack_from('>I',raw,gtf+12+36*3+4)[0]
        require(out[:gtf]==raw[:gtf] and out[off:]==raw[off:],'Final episode animation/background changed')
        return bytes(out),[]
    edits,counts=geometry(raw,member)
    for off,value in edits:out[off:off+len(value)]=value
    tile=Image.new('RGBA',(288,112));ink=word('Episode',font,110,(272,96))
    # Match the existing 50px-high quad to the 60px-high digit.
    ink=ink.resize((272,96),Image.Resampling.LANCZOS);tile.alpha_composite(ink,(8,8))
    for x,im in ((0,tile),(288,glow(tile))):paint(out,gtf,2,(x,0,288,112),im)
    paint(out,gtf,3,(0,0,1536,256),title_image(fallback,font))
    # Digit textures, backgrounds and everything after them must be identical.
    off=gtf+struct.unpack_from('>I',raw,gtf+12+36*4+4)[0]
    require(len(out)==len(raw) and out[off:]==raw[off:],'Episode digits/background changed')
    return bytes(out),counts


def prepare(asset,font):
    rows=catalog();mutations={};report=[]
    for mid,row in sorted(rows.items()):
        raw=asset(row['asset']);out=title_apply(raw,row,font);mutations[(TPACK,mid)]=out
        report.append({'asset':row['asset'],'source':row['source'],'english':row['english'],
                       'source_sha256':sha(raw),'output_sha256':sha(out)})
    for mid in EFFECTS:
        key='work/pkg/'+EFF+':'+str(mid);raw=asset(key)
        out,counts=effect_apply(raw,mid,font,rows[18 if mid==102 else 4]['english']);mutations[(EFF,mid)]=out
        report.append({'asset':key,'english':'Final Episode / '+rows[18]['english'] if mid==102 else 'Episode + native animated digits',
                       'source_sha256':sha(raw),'output_sha256':sha(out),'quad_counts':counts})
    return mutations,report


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true')
    ap.add_argument('--out',type=Path,default=ROOT/'work/chapter006_preview');args=ap.parse_args()
    out=args.out.resolve();require(ROOT/'work' in out.parents and not out.exists(),'Use a fresh work/ preview directory')
    rows=catalog()
    for mid,row in sorted(rows.items()):print(mid,row['source'],'->',row['english'])
    print('Episode headers: effect members 100, 101, 102; source texture previews and English contact sheet ->',out)
    if not args.write:print('DRY RUN');return
    out.mkdir(parents=True);c=CPK(str(ROOT/'work/pkg'/EFF))
    for mid in EFFECTS:
        raw=c.read(next(e for e in c.files if e['id']==mid));gtf=EFFECTS[mid][0]
        for tex,frame,im in textures(raw[gtf:]):
            if tex in (2,3):im.save(out/('source_%d_%d.png'%(mid,tex)))
        built,_=effect_apply(raw,mid,DEFAULT_FONT,rows[18 if mid==102 else 4]['english'])
        for tex,frame,im in textures(built[gtf:]):
            if tex==2:im.save(out/('english_%d_header.png'%mid))
    sheet=Image.new('RGB',(768,len(rows)*80),(12,20,26))
    for n,(mid,row) in enumerate(sorted(rows.items())):
        im=title_image(row['english'],DEFAULT_FONT).crop((0,0,1536,128)).resize((768,64))
        sheet.paste(im,(0,n*80),im)
    sheet.save(out/'titles.png')


if __name__=='__main__':main()
