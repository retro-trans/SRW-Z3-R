"""Build NPJB00689 English test assets for RPCS3 and CFW/HEN PS3.

Dry-run by default. --write requires a NEW directory under work/builds/.
The original extraction and sibling project are read-only inputs. This does
not install, boot an emulator, modify saves, or claim hardware testing.
"""
import argparse
import hashlib
from collections import Counter, defaultdict
import importlib.util
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import zipfile

import localization
import luarec
import non_dialogue as nd
import battle_lines as battle
import rengoku_screenshot_layout as screenshot_layout
import rengoku_search_layout as search_layout
import rengoku_roster_settings_layout as roster_settings_layout
import rengoku_command_layout as command_layout
import rengoku_map_panel_layout as map_panel_layout
import rengoku_battle_preview_layout as battle_preview_layout
import rengoku_battle_subtitles as battle_subtitles
import rengoku_result_layout as result_layout
import rengoku_battle_controls as battle_controls
import rengoku_intermission_layout as intermission_layout
import rengoku_narration as narration
import rengoku_chapter_art as chapter_art
import rengoku_title_art as title_art
import rengoku_library_chart as library_chart
from cpk import CPK
from source_text import lua_strings, byte_offsets, library_fields
from rengoku_runtime import Codec, align, font_pages, patch_elf, require, sha, DEFAULT_FONT

ROOT=Path(__file__).resolve().parents[1]
PKG=ROOT/'work/pkg'
BASE=ROOT.parent/'SRW Z3'


def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def document(x): return json.dumps(x,ensure_ascii=False,indent=2)+'\n'


def checked_output(p):
    p=p.resolve(); root=(ROOT/'work/builds').resolve()
    require(root in p.parents and p!=root, 'Output must be a new child of work/builds/')
    require(not p.exists(), 'Output exists; refusing to overwrite a build')
    return p


def controls(data):
    off,size=struct.unpack_from('>QQ',data,0x58);end=off+size;result={}
    require(end<=len(data),'SELF control table bounds')
    while off<end:
        kind,length,more=struct.unpack_from('>IIQ',data,off)
        require(length>=16 and off+length<=end and kind not in result,'SELF control record')
        result[kind]=(off,length);off+=length
        require(bool(more)==(off<end),'SELF control chain')
    return result


def wrap_self(elfpath,original,destination):
    tool=BASE/'work/cfw_psl1ght/fself.exe'
    result=subprocess.run([str(tool),'-n',str(elfpath),str(destination)],
                          capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
    require(result.returncode==0 and destination.is_file(),'NPDRM SELF wrapper failed: '+result.stderr.decode(errors='replace'))
    elf=elfpath.read_bytes();out=bytearray(destination.read_bytes())
    payload,size=struct.unpack_from('>QQ',out,16)
    require(out[:4]==b'SCE\0' and struct.unpack_from('>IHH',out,4)==(2,0x8000,1),'Fake SELF format')
    require(size==len(elf) and out[payload:]==elf,'SELF program payload changed')
    srcapp=struct.unpack_from('>Q',original,0x28)[0];app=struct.unpack_from('>Q',out,0x28)[0]
    require(struct.unpack_from('>I',original,srcapp+12)[0]==8,'Source is not NPDRM')
    out[app:app+32]=original[srcapp:srcapp+32]
    oldctrl,newctrl=controls(original),controls(out)
    for kind in (1,3):
        old,length=oldctrl[kind];new,newlength=newctrl[kind]
        require(length==newlength,'NPDRM metadata size mismatch')
        out[new+16:new+length]=original[old+16:old+length]
    require(b'JP0700-NPJB00689_00-SRWZ3RENDLGPKG00' in out[:payload],'Title identity missing')
    d=newctrl[2][0]
    require(out[d+36:d+56]==hashlib.sha1(elf).digest(),'SELF file digest mismatch')
    phoff=struct.unpack_from('>Q',elf,32)[0];n=struct.unpack_from('>H',elf,56)[0]
    eoff,poff=struct.unpack_from('>QQ',out,0x30)
    require(out[eoff:eoff+64]==elf[:64] and out[poff:poff+56*n]==elf[phoff:phoff+56*n],'Embedded ELF headers differ')
    sec=struct.unpack_from('>Q',out,0x48)[0]
    for i in range(n):
        row=struct.unpack_from('>IIQQQQQQ',elf,phoff+i*56)
        entry=struct.unpack_from('>QQIIII',out,sec+i*32)
        require(entry==(payload+row[2],row[5],1,0,0,2 if row[0]==1 else 0),'SELF load mapping mismatch')
    destination.write_bytes(out)
    return {'format':'NPDRM fake SELF for CFW/HEN and RPCS3; not retail signed',
            'tool_sha256':sha(tool.read_bytes()),'sha256':sha(out),'elf_payload_sha256':sha(elf),
            'title_id':'NPJB00689','source_application_and_capability_metadata_retained':True,
            'embedded_program_bytes_verified':True}


def load_cpk_writer():
    path=BASE/'tools/cpkpatch.py'
    spec=importlib.util.spec_from_file_location('rengoku_cpk_writer_reference',str(path))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def file_inventory(root):
    return {p.relative_to(root).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
            for p in sorted(root.rglob('*')) if p.is_file()}


def patch_sfo(raw,rows):
    out=bytearray(raw);keybase,base,n=struct.unpack_from('<III',raw,8)
    require(raw[:4]==b'\0PSF','SFO magic')
    for r in rows:
        found=False
        for i in range(n):
            p=20+16*i;ko,fmt,length,maximum,offset=struct.unpack_from('<HHIII',raw,p)
            key=raw[keybase+ko:raw.index(b'\0',keybase+ko)].decode()
            if not key.startswith('TITLE') or base+offset!=r['offset']:continue
            require(raw[base+offset:base+offset+length].rstrip(b'\0').decode('utf-8')==r['jp'],'SFO title source')
            value=r['english'].encode('utf-8')+b'\0'
            require(len(value)<=maximum,'SFO title slot too small')
            out[base+offset:base+offset+maximum]=value.ljust(maximum,b'\0')
            struct.pack_into('<I',out,p+4,len(value));found=True
        require(found,'SFO source occurrence not TITLE')
    return bytes(out)


class Build:
    def __init__(self, font):
        self.font=font
        self.glossary=localization.terms()
        self.source=read(ROOT/'source/non_dialogue.json')
        self.locale=read(nd.LOCALE)
        self.bsource=read(battle.SOURCE)
        self.blocale=read(battle.LOCALE)
        require(self.locale['source_catalog_sha256']==sha(nd.SOURCE.read_bytes()),'Non-dialogue source catalog changed')
        require(self.blocale['source_catalog_sha256']==sha(battle.SOURCE.read_bytes()),'Battle source catalog changed')
        self.occ={};self.bocc={};self.texts=[];self.routes={};self.asset_cache={}
        for source,locale,dest in [(self.source,self.locale,self.occ),(self.bsource,self.blocale,self.bocc)]:
            rows={r['id']:r for r in source['records']}
            for identity,v in locale['messages'].items():
                if v['status'].startswith('excluded_') or v['status']=='preserved_runtime':continue
                require(bool(v['text']), 'Missing English: '+identity)
                require(sha(v['source'].encode())==v['source_sha256'],'Source text changed: '+identity)
                for oid in v['occurrences']:
                    r=rows[oid]
                    require(r['jp']==v['source'],'Occurrence source changed')
                    en=nd.validate_target(v['source'],nd.occurrence_text(v,oid),self.glossary)
                    dest[oid]=dict(r,english=en,message=identity)
                    self.texts.append(en)
        self.story={};self.story_rows={}
        rows,catalog=localization.load_catalog()
        for identity,row in rows.items():
            v=catalog[row['member']]['messages'][identity]
            errors,_=localization.validate(row,v,self.glossary)
            require(not errors and v.get('text'),identity+': '+repr(errors))
            en=localization.expand(v['text'],self.glossary)
            self.story[identity]=en;self.story_rows[identity]=row;self.texts.append(en)
        self.tpack=CPK(str(PKG/'USRDIR/DATA_REN/TABATA/TPACKPS3.CPK'))
        self.codec=Codec(self.texts,font_pages(self.tpack),font)
        for text in self.texts:self.codec.encode(text)
        self.byasset=defaultdict(list)
        for r in self.occ.values():self.byasset[r['asset']].append(r)
        self.conflicts=[];self.hooks={};self.hook_sources=defaultdict(list)
        candidate=defaultdict(set)
        # Exact draw-time matching keeps lookup keys and fixed-size gameplay
        # records intact. English lives outside every original text buffer.
        for r in list(self.occ.values())+list(self.bocc.values()):
            jp=r['jp'].replace('\r\n','\n');en=r['english']
            candidate[jp].add(en);self.hook_sources[jp].append(r['id'])
        for jp,options in candidate.items():
            if len(options)>1:
                self.conflicts.append({'source':jp,'english':sorted(options),'occurrences':self.hook_sources[jp]})
                continue
            en=next(iter(options))
            try:key=jp.encode('cp932')
            except UnicodeEncodeError:continue
            if key and b'\0' not in key:self.hooks[key]=self.codec.encode(en)
        # Whole-line matches support consumers that split multiline text. Only
        # exact unambiguous pairs with unchanged line counts are eligible.
        linepairs=defaultdict(set)
        for jp,options in candidate.items():
            if len(options)!=1:continue
            en=next(iter(options));js=jp.split('\n');es=en.split('\n')
            if len(js)!=len(es) or len(js)<2:continue
            for a,b in zip(js,es):
                if len(a)>=6 and b:linepairs[a].add(b)
        for jp,options in linepairs.items():
            if len(options)!=1 or jp in candidate:continue
            try:key=jp.encode('cp932')
            except UnicodeEncodeError:continue
            self.hooks[key]=self.codec.encode(next(iter(options)))
        self.original_elf=(ROOT/'work/eboot/EBOOT.ELF').read_bytes()
        self.srvc,self.srvc_edit,self.battle_report=self.make_srvc()
        self.elf_edits=[self.srvc_edit]
        self.elf_edits+=screenshot_layout.native_movement_fields(self.original_elf,self.codec)
        self.hooks.update(screenshot_layout.hooks(self.codec,self.locale['messages']))
        # These long UTF-8 messages contain PSN/PlayStation symbols that the
        # game's CP932 drawer cannot represent. They are native system-dialog
        # prose; retain ordinary UTF-8, not the custom atlas codec. Full English
        # must fit the existing field or it stays explicitly pending.
        for r in self.occ.values():
            if r['asset']!='work/eboot/EBOOT.ELF' or r.get('encoding')!='utf-8':continue
            title=r['id']=='nd:546dfaa5027410b17cad'
            if not title:
                try:r['jp'].encode('cp932');continue
                except UnicodeEncodeError:pass
                require(len(r['jp'])>=25,'Unexpected short native Unicode symbol label')
            old=r['jp'].encode('utf-8')+b'\0';new=r['english'].encode('utf-8')+b'\0'
            if len(new)>len(old):continue
            self.elf_edits.append((r['offset'],old,new.ljust(len(old),b'\0'),'native UTF-8 system-dialog message '+r['id']))
            self.routes[r['id']]='native UTF-8 title field' if title else 'native UTF-8 system-dialog field'
        self.elf,self.runtime=patch_elf(self.original_elf,self.codec,self.hooks,self.elf_edits)
        self.mutations={};self.asset_reports=[]

    def asset(self,key):
        if key not in self.asset_cache:
            name,colon,member=key.partition(':')
            path=ROOT/name
            if colon:
                cpk=CPK(str(path)); matches=[e for e in cpk.files if e['id']==int(member)]
                require(len(matches)==1,'Missing source member '+key)
                b=cpk.read(matches[0])
            else:b=path.read_bytes()
            self.asset_cache[key]=b
        return self.asset_cache[key]

    def verify_assets(self):
        checked={}
        for r in list(self.occ.values())+list(self.bocc.values()):
            if r['asset'] not in checked:checked[r['asset']]=sha(self.asset(r['asset']))
            require(checked[r['asset']]==r['asset_sha256'],'Source asset changed: '+r['asset'])

    def mark(self,rows,route):
        for r in rows:self.routes[r['id']]=route

    def make_srvc(self):
        original=(PKG/'USRDIR/DATA_REN/BTLC/SRVC.BIN').read_bytes()
        at,table,blocks=battle.discover_table(original,self.original_elf)
        require(at==self.bsource['table_offset'] and table==self.bsource['table'],'Battle bank table changed')
        edits={r['offset']:r for r in self.bocc.values() if isinstance(r.get('bank'),int)}
        display,self.subtitle_report=battle_subtitles.layout(self.codec,list(self.bocc.values()))
        output=bytearray();newtable=[0];count=0
        for b in blocks:
            header=bytearray(original[b['base']:b['pool']]);pool=bytearray();where={}
            indexed={b['pool']+struct.unpack_from('<I',original,b['index']+i*4)[0] for i in range(b['count'])}
            pos=b['pool']
            while pos<b['end']:
                stop=original.index(b'\0',pos,b['end'])
                old=original[pos:stop]
                if old or pos in indexed:
                    where[pos]=len(pool)
                    if pos in edits:
                        row=edits[pos];require(old.decode('cp932')==row['jp'],'Battle binding changed')
                        pool+=self.codec.encode(display[pos])+b'\0';count+=1
                        self.routes[row['id']]='rebuilt SRVC bank/index'
                    else:pool+=old+b'\0'
                pos=stop+1
            for i in range(b['count']):
                old=b['pool']+struct.unpack_from('<I',original,b['index']+i*4)[0]
                require(old in where,'Lost battle cue')
                struct.pack_into('<I',header,b['index']-b['base']+i*4,where[old])
            output+=header+pool;output+=bytes(align(len(output))-len(output));newtable.append(len(output))
        old=struct.pack('>%dI'%len(table),*table);new=struct.pack('>%dI'%len(newtable),*newtable)
        # Verify every cue independently through the reconstructed bank table.
        for b,base,end in zip(blocks,newtable,newtable[1:]):
            po=base+b['pool']-b['base'];idx=base+b['index']-b['base']
            require(output[base:idx]==original[b['base']:b['index']],'Battle cue metadata changed')
            for i in range(b['count']):
                oldoff=b['pool']+struct.unpack_from('<I',original,b['index']+i*4)[0]
                newoff=po+struct.unpack_from('<I',output,idx+i*4)[0]
                require(po<=newoff<end,'New battle pointer out of bounds')
                want=self.codec.encode(display[oldoff]) if oldoff in edits else original[oldoff:original.index(b'\0',oldoff)]
                require(output[newoff:output.index(0,newoff,end)]==want,'Battle cue text mismatch')
        summary={k:v for k,v in self.subtitle_report.items() if k not in ('changed','pending')}
        summary['pending_messages']=len(self.subtitle_report['pending'])
        summary['examples']=self.subtitle_report['changed'][:3]+[r for r in self.subtitle_report['changed'] if r['message']=='battle:bb4a3ab0560dceda']
        return bytes(output),(at,old,new,'Rengoku SRVC bank offsets'),{'banks':len(blocks),'translated_occurrences':count,'indexed_cues':sum(b['count'] for b in blocks),'source_bytes':len(original),'output_bytes':len(output),'subtitle_layout':summary}

    def lua(self,raw,asset,member=None):
        text=raw.decode('cp932');offsets=byte_offsets(text);spans={};rows=self.byasset.get(asset,[])
        literals=list(lua_strings(text))
        for r in rows:
            matches=[x for x in literals if offsets[x['content_start']]==r['offset']]
            require(len(matches)==1,'Lua occurrence not a literal boundary: '+r['id'])
            x=matches[0];spans[(x['content_start'],x['content_end'])]=(r['english'],x['kind'],r['id'])
        if member:
            src=read(ROOT/'source/story'/ (member+'.json'))
            require(sha(raw)==src['sha256'],'Story member changed: '+member)
            long=list(luarec.BLOCK.finditer(text))
            require(len(long)==len(src['records']),'Story block count changed')
            for m,r in zip(long,src['records']):
                require(luarec.digest(m[1])==r['sha'],'Story source fingerprint changed')
                spans[(m.start(1),m.end(1))]=(self.story[r['id']],'long',r['id'])
        result=bytearray();pos=0
        for (start,end),(en,kind,identity) in sorted(spans.items()):
            require(start>=pos,'Overlapping Lua edits')
            result+=raw[offsets[pos]:offsets[start]]
            encoded=self.codec.encode(en,newline='\r\n' if kind=='long' else '\n')
            if kind=='quoted':
                # Escape each byte only at character boundaries. A CP932 trail
                # byte 0x5c must also be escaped for Lua's byte lexer.
                quote=text[start-1].encode('ascii')
                encoded=encoded.replace(b'\\',b'\\\\').replace(quote,b'\\'+quote).replace(b'\r',b'\\r').replace(b'\n',b'\\n')
            else:require(b']]' not in encoded,'Encoded Lua closes a long string')
            result+=encoded;pos=end;self.routes[identity]='rebuilt Lua literal'
        result+=raw[offsets[pos]:]
        for r in rows:
            if r['id'] not in self.routes:self.routes[r['id']]='overlapping canonical story literal'
        return bytes(result)

    def library(self,raw,rows):
        magic,fields=library_fields(raw)
        decoded=bytes(c if c in (0,0x5e) else c^0x5e for c in raw)
        lookup={r['locator']:r for r in rows};body=bytearray()
        for f in fields:
            payload=decoded[f['offset']:f['offset']+f['bytes']]
            if f['tag'] in lookup:
                r=lookup[f['tag']];require(f['text']==r['jp'],'Library field source changed')
                target=screenshot_layout.library_text(self.codec,f['tag'],r['english'])
                payload=self.codec.encode(target)+(b'\0' if payload.endswith(b'\0') else b'')
                self.routes[r['id']]='rebuilt library field'
            body+=f['tag'].encode()+struct.pack('<I',len(payload))+payload
        out=decoded[:16]+b'DSIZ'+struct.pack('<I',len(body)+8)+b'DATA'+struct.pack('<I',len(body))+body
        return bytes(c if c in (0,0x5e) else c^0x5e for c in out)

    def indexed(self,raw,rows):
        size=struct.unpack_from('>I',raw,24)[0];tdxt=32+size;base=tdxt+16
        require(raw[tdxt:tdxt+4]==b'TDXT' and base+struct.unpack_from('>I',raw,tdxt+8)[0]==len(raw),'Indexed text bounds')
        out=bytearray(raw[:base]);body=bytearray();lookup={int(r['locator'].split(':')[1]):r for r in rows}
        for i in range(size//4):
            off=base+struct.unpack_from('>I',raw,32+i*4)[0];end=raw.index(b'\0',off);value=raw[off:end]
            if i in lookup:
                r=lookup[i];require(value.decode(r['encoding'])==r['jp'],'Indexed source changed')
                target=screenshot_layout.text_for_field(r['jp'],r['english'])
                value=self.codec.encode(target,utf8=r['encoding']=='utf-8');self.routes[r['id']]='rebuilt indexed text'
            struct.pack_into('>I',out,32+i*4,len(body));body+=value+b'\0'
        struct.pack_into('>I',out,tdxt+8,len(body));out+=body
        for i,r in lookup.items():
            off=base+struct.unpack_from('>I',out,32+i*4)[0]
            target=screenshot_layout.text_for_field(r['jp'],r['english'])
            require(out[off:out.index(0,off)]==self.codec.encode(target,utf8=r['encoding']=='utf-8'),'Indexed readback')
        return bytes(out)

    def mtfl(self,raw,rows):
        fields=list(nd.mtfl_fields(raw));n=struct.unpack_from('<I',raw,0x40)[0]
        byfield={(r['entry'],r['locator'].split(':')[1]):r for r in rows}
        pos=0x44;index=[]
        for _ in range(n):
            values=struct.unpack_from('<8I',raw,pos);mark,identity=struct.unpack_from('<II',raw,pos+32)
            require(mark==0xffffffff,'MTFL index marker');index.append((identity,pos,values));pos+=40
        base=pos+16;minimum=min(v[i] for _,_,v in index for i in (0,2,4,6))
        last=max(v[i]+v[i+1] for _,_,v in index for i in (0,2,4,6))
        marker=raw.find(b'ENDoMTFLs',base+last-1)
        require(marker>=0,'MTFL footer missing')
        head=bytearray(raw[:base]);body=bytearray(raw[base:base+minimum]);where={}
        xor=lambda data:bytes(c if c==0x7a else c^0x7a for c in data)
        for identity,p,values in index:
            updated=[]
            for j,tag in enumerate(('WORD','SRCE','DSCR','DSC2')):
                off,length=values[j*2:j*2+2];value=xor(raw[base+off:base+off+length])
                if (identity,tag) in byfield:
                    r=byfield[(identity,tag)];require(value.decode('cp932')==r['jp'],'MTFL source binding')
                    value=self.codec.encode(screenshot_layout.library_text(self.codec,tag,r['english']));self.routes[r['id']]='rebuilt keyword library field'
                if value not in where:where[value]=len(body);body+=xor(value)+b'\0'
                updated += [where[value],len(value)]
            struct.pack_into('<8I',head,p,*updated)
        # The original terminator directly follows the final field (no NUL).
        body=body[:-1];out=head+body+raw[marker:];newmarker=len(head)+len(body)
        for p,expected in [(0x10,marker-0x20),(0x24,marker-0x20),(0x2c,marker-0x30)]:
            require(struct.unpack_from('<I',raw,p)[0]==expected,'MTFL size-word layout changed')
            struct.pack_into('<I',out,p,expected+newmarker-marker)
        j=raw.find(b'jstr',pos-16,base+16)
        require(j>=0,'MTFL jstr descriptor missing')
        require(struct.unpack_from('<II',raw,j+8)[1]==marker-(j+16),'MTFL jstr body size')
        struct.pack_into('<I',out,j+4,newmarker-(j+16)+16)
        struct.pack_into('<I',out,j+12,newmarker-(j+16))
        for identity,p,values in index:
            for j,tag in enumerate(('WORD','SRCE','DSCR','DSC2')):
                off,length=struct.unpack_from('<II',out,p+j*8)
                oldoff,oldlength=values[j*2:j*2+2]
                want=self.codec.encode(screenshot_layout.library_text(self.codec,tag,byfield[(identity,tag)]['english'])) if (identity,tag) in byfield else xor(raw[base+oldoff:base+oldoff+oldlength])
                require(xor(out[base+off:base+off+length])==want,'MTFL field readback')
        return bytes(out)

    def credits(self,raw,rows):
        fields=dict(nd.credit_fields(raw));out=bytearray(raw)
        for r in rows:
            if r['offset'] not in fields:continue
            require(fields[r['offset']]==r['jp'],'Credit field source')
            value=self.codec.encode(r['english'])+b'\0'
            if len(value)>64:continue # Long names use owned draw-time storage.
            p=r['offset'];out[p:p+64]=value.ljust(64,b'\0')
            self.routes[r['id']]='fixed credit display field'
        return bytes(out)

    def fssa(self,raw,rows):
        start,end=struct.unpack_from('>II',raw,0x20)
        records,record_end=struct.unpack_from('>II',raw,0x48)
        require(raw[:4]==b'FSSA' and (record_end-records)%32==0 and records>=end,'FSSA record section')
        starts={0};p=start
        while p<end:
            q=raw.index(b'\0',p,end);starts.add(p-start);p=q+1
        refs=defaultdict(list)
        for p in range(records,record_end,32):
            off=struct.unpack_from('>I',raw,p)[0]
            require(off in starts and off<end-start,'FSSA text record does not point to a string start')
            # +12 is a color/style word, not a fixed separator. Pointer
            # membership is validated for EVERY row in the declared section.
            refs[start+off].append(p)
        out=bytearray(raw);done=[]
        for r in rows:
            off=r['offset']
            if off not in refs:continue
            old=raw[off:raw.index(b'\0',off,end)]
            require(old.decode(r['encoding'])==r['jp'],'FSSA source changed')
            target=screenshot_layout.text_for_field(r['jp'],r['english'])
            new=self.codec.encode(target,utf8=r['encoding']=='utf-8')+b'\0'
            dest=len(out);out+=new
            for p in refs[off]:struct.pack_into('>I',out,p,dest-start)
            done.append((r,refs[off],dest,new));self.routes[r['id']]='relocated FSSA text record'
        allowed={p+i for _,refs_,_,_ in done for p in refs_ for i in range(4)}
        require(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,out))),'Unexpected FSSA metadata change')
        for r,refs_,dest,new in done:
            for p in refs_:
                off=start+struct.unpack_from('>I',out,p)[0]
                require(out[off:off+len(new)]==new,'FSSA relocation readback')
        out,self.layout_report=screenshot_layout.apply_fssa(raw,out,self.codec)
        out,self.search_layout_report=search_layout.apply_fssa(raw,out,self.codec)
        out,self.roster_settings_report=roster_settings_layout.apply_fssa(raw,out,self.codec)
        out,self.command_layout_report=command_layout.apply_fssa(raw,out,self.codec)
        out,self.map_panel_report=map_panel_layout.apply_fssa(raw,out,self.codec)
        out,self.battle_preview_report=battle_preview_layout.apply_fssa(
            raw,out,self.codec,self.asset(battle_preview_layout.STYLE_ASSET))
        out,self.result_layout_report=result_layout.apply_fssa(raw,out,self.codec)
        out,self.battle_controls_report=battle_controls.apply_fssa(
            raw,out,self.codec,self.asset(battle_controls.STYLE_ASSET))
        out,self.intermission_report=intermission_layout.apply_fssa(raw,out,self.codec)
        self.intermission_review=intermission_layout.review(raw)
        return out

    def prepare(self):
        print('Verifying original asset fingerprints...',flush=True)
        self.verify_assets()
        print('Rebuilding source-bound Lua and library/menu members in memory...',flush=True)
        stage=CPK(str(ROOT/'work/story/STGZ3REN.cpk'))
        for e in stage.files:
            member='STGZ3REN_%05d'%e['id'];p=ROOT/'work/story'/(member+'.lua')
            if p.exists():
                raw=stage.read(e);require(raw==p.read_bytes(),'Stage extraction changed')
                output=self.lua(raw,'work/story/'+p.name,member)
                if output!=raw:self.mutations[('USRDIR/DATA_REN/STAGE/STGZ3REN.SDAT',e['id'])]=output
        self.narration_hooks={};self.narration_report=[]
        for asset,rows in self.byasset.items():
            if asset.startswith('work/story/') or ':' not in asset:continue
            name,mid=asset.rsplit(':',1);mid=int(mid);raw=self.asset(asset);out=raw
            if '/MTZKN_' in name:out=self.library(raw,rows)
            elif name.endswith('MTV_ALL_KEYWORD_DEF.CPK'):out=self.mtfl(raw,rows)
            elif name.endswith('LUACPKZ3REN.CPK'):out=self.lua(raw,asset)
            elif name.endswith('AIDDATAPACK_R.CPK'):
                if mid in (5,6):out=self.indexed(raw,rows)
                elif mid==0:out=self.fssa(raw,rows)
                elif mid==15:out=self.credits(raw,rows)
                elif mid in (13,14):
                    out,hooks,proof=narration.apply(raw,rows,self.codec,mid)
                    self.narration_hooks.update(hooks);self.narration_report.append(proof)
                    self.mark(rows,'timed narration with measured bounds and owned draw text')
            if out!=raw:
                relative=Path(name).relative_to('work/pkg').as_posix()
                self.mutations[(relative,mid)]=out
                self.asset_reports.append({'asset':asset,'source_bytes':len(raw),'output_bytes':len(out),'source_sha256':sha(raw),'output_sha256':sha(out)})
        for mid,b in self.codec.patched_pages().items():
            self.mutations[('USRDIR/DATA_REN/TABATA/TPACKPS3.CPK',mid)]=b
        art,self.art_report=chapter_art.prepare(self.asset,self.font)
        require(not set(art).intersection(self.mutations),'Artwork overwrites another insertion')
        self.mutations.update(art)
        title,self.title_art_report=title_art.prepare(self.asset)
        require(not set(title).intersection(self.mutations),'Title artwork overwrites another insertion')
        self.mutations.update(title)
        library,self.library_chart_report=library_chart.prepare(self.asset,title[(title_art.EFF,title_art.MEMBER)],self.font)
        require(set(library).intersection(self.mutations)=={(title_art.EFF,title_art.MEMBER)},'Unexpected Library/chart insertion collision')
        self.mutations.update(library)
        art_key=(intermission_layout.AID,1)
        require(art_key not in self.mutations,'Intermission atlas insertion collision')
        self.mutations[art_key]=intermission_layout.apply_art(
            self.asset('work/pkg/'+intermission_layout.AID+':1'),self.font)
        # Resolve homographs after source-specific fields were inserted. The
        # remaining draw-time consumers must all agree before adding a key.
        remaining=defaultdict(set)
        for r in list(self.occ.values())+list(self.bocc.values()):
            if r['id'] not in self.routes and r['asset']!='work/pkg/PARAM.SFO':
                remaining[r['jp'].replace('\r\n','\n')].add(r['english'])
        for jp,options in remaining.items():
            if len(options)!=1:continue
            try:key=jp.encode('cp932')
            except UnicodeEncodeError:continue
            if key and b'\0' not in key:self.hooks[key]=self.codec.encode(next(iter(options)))
        sfo_rows=self.byasset.get('work/pkg/PARAM.SFO',[])
        self.sfo=patch_sfo((PKG/'PARAM.SFO').read_bytes(),sfo_rows)
        self.mark(sfo_rows,'rebuilt SFO title metadata')
        for r in list(self.occ.values())+list(self.bocc.values()):
            if r['id'] in self.routes:continue
            jp=r['jp'].replace('\r\n','\n')
            try:key=jp.encode('cp932')
            except UnicodeEncodeError:key=b''
            if key in self.hooks and self.hooks[key]==self.codec.encode(r['english']):
                self.routes[r['id']]='exact draw-time table; runtime consumer unverified'
            else:self.routes[r['id']]='pending consumer-specific insertion'
        pending=[dict(id=r['id'],message=r['message'],asset=r['asset'],source=r['jp'],english=r['english'])
                 for r in list(self.occ.values())+list(self.bocc.values())
                 if self.routes[r['id']]=='pending consumer-specific insertion']
        self.hooks.update(screenshot_layout.hooks(self.codec,self.locale['messages']))
        self.hooks.update(screenshot_layout.chapter_hooks(self.codec,self.occ.values()))
        chart_hooks,self.chart_title_report=library_chart.chapter_hooks(self.codec,self.occ.values(),self.original_elf)
        self.hooks.update(chart_hooks)
        self.hooks.update(self.narration_hooks)
        self.hooks.update(map_panel_layout.hooks(self.codec))
        effects,self.effect_layout_report=search_layout.effect_hooks(
            self.asset(search_layout.RPW_ASSET),self.byasset[search_layout.RPW_ASSET],self.codec)
        self.hooks.update(effects)
        self.elf,self.runtime=patch_elf(self.original_elf,self.codec,self.hooks,self.elf_edits)
        return {'title_id':'NPJB00689','targets':['RPCS3','PS3 CFW/HEN'],
                'story_records':len(self.story),'battle':self.battle_report,
                'font_glyphs':len(self.codec.codes),'hook_pairs':len(self.hooks),
                'font_sources':self.codec.font_sources,
                'font_recipe':{'face':'Rodin Latin Bold','cap_height':22,'baseline':26,'supersampling':4,'stem_thickening':0.5},
                'screenshot_layout':self.layout_report,
                'search_layout':self.search_layout_report,
                'roster_settings_layout':self.roster_settings_report,
                'command_layout':self.command_layout_report,
                'map_panel_layout':self.map_panel_report,
                'battle_preview_layout':self.battle_preview_report,
                'result_layout':self.result_layout_report,
                'battle_controls':self.battle_controls_report,
                'combo_popup':self.runtime['combo_popup'],
                'intermission_layout':self.intermission_report,
                'intermission_review':{k:v for k,v in self.intermission_review.items() if k!='rows'},
                'effect_layout':self.effect_layout_report,
                'narration_layout':self.narration_report,
                'chapter_artwork':self.art_report,
                'title_artwork':self.title_art_report,
                'library_chart_artwork':self.library_chart_report,
                'chart_chapter_titles':self.chart_title_report,
                'font_mapping':{c:{'cp932':'%04X'%code,'unicode':'%04X'%self.codec.unicode[c]}
                                for c,code in self.codec.codes.items()},
                'archive_members_rebuilt':len(self.mutations),'routes':dict(Counter(self.routes.values())),
                'pending':pending,'conflicts':self.conflicts,'runtime':self.runtime,
                'artwork':'English Intermission heading in AID 1; title and five Library labels inserted in EFF 133; chart heading/background in EFF 131/132; 15 chapter title blocks and single/double/final episode animations inserted; other 166 cataloged blocks pending raster insertion',
                'rpcs3_gameplay_tested':False,'ps3_hardware_tested':False}

    def write(self,out,report):
        version=out.name.rsplit('_',1)[-1]
        inputs=file_inventory(PKG)
        locales=file_inventory(ROOT/'localization')
        out.mkdir(parents=True)
        intermediate=out/'intermediate';intermediate.mkdir()
        tree=out/'RPCS3/NPJB00689'
        print('Creating a separate complete game folder...',flush=True)
        shutil.copytree(PKG,tree)
        changed={};groups=defaultdict(dict)
        for (path,mid),raw in self.mutations.items():groups[path][mid]=raw
        writer=load_cpk_writer();npdata=ROOT/'work/toolchain/make_npdata.exe'
        for number,(relative,replacements) in enumerate(sorted(groups.items())):
            dest=tree/relative;stage=relative.endswith('.SDAT')
            source=ROOT/'work/story/STGZ3REN.cpk' if stage else PKG/relative
            job=intermediate/('archive_%02d'%number);job.mkdir()
            files={}
            for mid,raw in replacements.items():
                p=job/('%05d.bin'%mid);p.write_bytes(raw);files[mid]=str(p)
            rebuilt=job/'rebuilt.cpk'
            writer.build(str(source),str(rebuilt),files)
            writer.validate_itoc(rebuilt.read_bytes())
            before,after=CPK(str(source)),CPK(str(rebuilt))
            require([e['id'] for e in before.files]==[e['id'] for e in after.files],'CPK member IDs changed')
            for a,b in zip(before.files,after.files):
                want=replacements[a['id']] if a['id'] in replacements else before.read(a)
                require(after.read(b)==want,'CPK readback failed: '+relative+':'+str(a['id']))
                if a['id'] not in replacements:
                    require(before.buf[a['offset']:a['offset']+a['size']]==after.buf[b['offset']:b['offset']+b['size']],
                            'Untouched compressed CPK member changed')
            if stage:
                encrypted=job/'STGZ3REN.SDAT'
                result=subprocess.run([str(npdata),'-e',str(rebuilt),str(encrypted),'2','0','00','1','16','0','','0'],
                    capture_output=True,timeout=90,creationflags=subprocess.CREATE_NO_WINDOW)
                (job/'encrypt.log').write_bytes(result.stdout+result.stderr)
                require(result.returncode==0 and encrypted.exists(),'SDAT encryption failed')
                plain=job/'roundtrip.cpk'
                result=subprocess.run([str(npdata),'-d',str(encrypted),str(plain),'0'],
                    capture_output=True,timeout=90,creationflags=subprocess.CREATE_NO_WINDOW)
                (job/'decrypt.log').write_bytes(result.stdout+result.stderr)
                require(result.returncode==0 and plain.read_bytes()==rebuilt.read_bytes(),'SDAT round-trip mismatch')
                shutil.copyfile(encrypted,dest)
            else:shutil.copyfile(rebuilt,dest)
            changed[relative]={'bytes':dest.stat().st_size,'sha256':sha(dest.read_bytes()),'replaced_members':sorted(replacements)}
            print('Verified',relative,':',len(replacements),'rebuilt members',flush=True)
        srvc=tree/'USRDIR/DATA_REN/BTLC/SRVC.BIN';srvc.write_bytes(self.srvc)
        (tree/'PARAM.SFO').write_bytes(self.sfo)
        elfpath=intermediate/'EBOOT.ELF';elfpath.write_bytes(self.elf)
        wrapped=intermediate/'EBOOT.BIN'
        report['self']=wrap_self(elfpath,(PKG/'USRDIR/EBOOT.BIN').read_bytes(),wrapped)
        shutil.copyfile(wrapped,tree/'USRDIR/EBOOT.BIN')
        # Store a font proof without claiming it is a runtime screenshot.
        preview=self.font_preview();preview.save(out/'font_preview.png')
        title=self.mutations[(title_art.EFF,title_art.MEMBER)]
        title_art.composition(title).save(out/'title_preview_large.png')
        title_art.composition(title,True).save(out/'title_preview_menu.png')
        library_chart.atlas(title,title_art.GTF,5).save(out/'library_buttons_preview.png')
        chart=self.mutations[(library_chart.EFF,131)]
        library_chart.chart_proof(chart,self.codec).save(out/'chart_preview.png')
        longest=max(self.chart_title_report,key=lambda r:r['width_at_36px'])
        library_chart.chart_proof(chart,self.codec,'Episode 10',longest['english']).save(out/'chart_longest_title_preview.png')
        final=file_inventory(tree)
        require(set(final)==set(inputs),'Game file inventory changed')
        differences=[p for p in final if final[p]!=inputs[p]]
        expected=set(groups)|{'USRDIR/DATA_REN/BTLC/SRVC.BIN','USRDIR/EBOOT.BIN','PARAM.SFO'}
        require(set(differences)==expected,'Unexpected output files changed')
        overlay=out/'PS3/NPJB00689'
        for relative in differences:
            dest=overlay/relative;dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(tree/relative,dest)
        report['game_files']=final;report['changed_files']=differences
        report['source_files']=inputs;report['locale_inputs']=locales
        report['asset_builds']=self.asset_reports
        report['source_files_preserved']=file_inventory(PKG)==inputs
        report['catalogs_preserved']=file_inventory(ROOT/'localization')==locales
        require(report['source_files_preserved'] and report['catalogs_preserved'],'An input changed during build')
        report['source_pkg_sha256']='77431599e49115ee14070d11df910ea48d5f3c812883870d9770755d15400307'
        report['archive_readback_verified']=True;report['sdat_roundtrip_verified']=True
        instructions=(
            '# SRW Z3 Rengoku-hen English test build '+version+'\n\n'
            'Target: PS3 NPJB00689. This is a test build, not a verified release.\n\n'
            '## RPCS3\n\n'
            'Use File > Boot Game and select RPCS3/NPJB00689. The complete game\n'
            'folder includes the translated files and an NPDRM fake SELF. Keep\n'
            'your existing game/license setup; this build does not include a RAP.\n'
            'Install your own matching JP0700-NPJB00689_00-SRWZ3RENDLGPKG00.rap\n'
            'in the emulator folder at dev_hdd0/home/<active-user>/exdata/.\n'
            'The original DATA01.EDAT still requires this license; error 80029521\n'
            'means RPCS3 could not find it. Restart the game after installation.\n\n'
            '## PS3 with CFW or HEN\n\n'
            'Install and activate the matching original NPJB00689 game first.\n'
            'Back up the matching files, then copy the contents of PS3/NPJB00689\n'
            'over /dev_hdd0/game/NPJB00689/ while the game is closed. All remaining\n'
            'files come from your existing installation. Enable HEN if applicable.\n'
            'The patch ZIP contains this same overlay; no save files are included.\n\n'
            '## What is verified\n\n'
            'All changed CPK members were read back, untouched archive members\n'
            'match their originals, the stage SDAT decrypts back to the rebuilt\n'
            'archive, and all 6,356 battle cue pointers resolve to their expected\n'
            'strings. Executable code edits are guarded against the Rengoku ELF.\n'
            'Both targets use the same assets and wrapped executable.\n\n'
            '## What still needs testing\n\n'
            'Gameplay, real console loading, screen fit, typewriter timing and\n'
            'every draw-time menu lookup have not been verified in game.\n'
            'Title previews show sprite fit, not a captured running game;\n'
            'check the large logo, smaller menu logo and their transitions.\n'
            'All 15 chapter title images and episode headers are translated.\n'
            'Both title-screen states use English wordmark/subtitle sprites.\n'
            'Other raster artwork/manual translations remain pending. See\n'
            'BUILD_REPORT.json for exact insertion coverage and pending cases.\n'
            'Existing translation review flags remain.\n')
        (out/'README.md').write_text(instructions,encoding='utf-8')
        archive=out/('SRW_Z3_Rengoku_English_'+version+'_PS3_RPCS3_overlay.zip')
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for relative in differences:z.write(overlay/relative,'NPJB00689/'+relative)
            z.writestr('README.md',instructions)
        with zipfile.ZipFile(archive) as z:
            require(z.testzip() is None,'Patch ZIP CRC failed')
            for relative in differences:require(sha(z.read('NPJB00689/'+relative))==final[relative]['sha256'],'Patch ZIP readback failed')
        report['patch_zip']={'name':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive.read_bytes())}
        (out/'BUILD_REPORT.json').write_text(document(report),encoding='utf-8')
        (out/'SUBTITLE_LAYOUT.json').write_text(document(self.subtitle_report),encoding='utf-8')
        (out/'INTERMISSION_REVIEW.json').write_text(document(self.intermission_review),encoding='utf-8')
        intermission_layout.header_tile(self.font).save(out/'intermission_heading_preview.png')
        (out/'SHA256SUMS.txt').write_text('\n'.join(final[p]['sha256']+'  NPJB00689/'+p for p in differences)+'\n'+report['patch_zip']['sha256']+'  '+archive.name+'\n',encoding='utf-8')
        print('Built and verified:',out,flush=True)

    def font_preview(self):
        from PIL import Image,ImageDraw
        glyphs=list(self.codec.glyphs.items());cols=16;rows=(len(glyphs)+cols-1)//cols
        im=Image.new('RGB',(cols*48,rows*56),(24,27,32));d=ImageDraw.Draw(im)
        for i,(code,glyph) in enumerate(glyphs):
            x,y=(i%cols)*48,(i//cols)*56
            im.paste((240,240,240),(x+8,y+2,x+40,y+34),glyph)
            d.text((x+5,y+36),'%04X'%code,fill=(170,190,210))
        return im


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,default=ROOT/'work/builds/rengoku_en_001')
    ap.add_argument('--font',type=Path,default=DEFAULT_FONT)
    ap.add_argument('--write',action='store_true')
    args=ap.parse_args();out=checked_output(args.out)
    print('Checking canonical English and Rengoku source bindings...',flush=True)
    build=Build(args.font);report=build.prepare()
    print(document({k:v for k,v in report.items() if k not in ('runtime','conflicts','pending','font_mapping')}))
    print('Pending consumer-specific insertion:',len(report['pending']))
    for p in report['pending']:print(p['id'],p['asset'],repr(p['source'][:50]),'->',repr(p['english'][:65]))
    print('Story sample:',next(iter(build.story.values())))
    print('New output:',out)
    if not args.write:
        print('DRY RUN: no game files written. --write creates the inspected build in a new directory.')
        return
    build.write(out,report)


if __name__=='__main__':main()
