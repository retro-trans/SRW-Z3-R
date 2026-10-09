"""Source-bound battle subtitles. Story scripts and original binaries are never written."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import struct
from cpk import CPK
from non_dialogue import ROOT, PKG, digest, encoded, scan_nul, validate_target
from source_text import rpw_strings
import localization

SOURCE=ROOT/'source/battle_lines.json'
LOCALE=ROOT/'localization/locales/en/battle_lines.json'
BINARY_CANDIDATES={'battle:91dc447d8efb8c34':' #ｰ','battle:c419cc1597729e6c':' #ﾀ'}


def parse_blocks(raw, table):
    if table[0]!=0 or table[-1]!=len(raw) or any(a>=b or a%16 or b%16 for a,b in zip(table,table[1:])):
        raise ValueError('Invalid battle bank boundaries')
    blocks=[]
    for bank,(base,end) in enumerate(zip(table,table[1:])):
        if base+8>end or raw[base]!=3:
            raise ValueError('Invalid battle bank header')
        n1,n2,n3=raw[base+1:base+4]
        n4,count=struct.unpack_from('<HH',raw,base+4)
        cues=base+8+n1*4+n4*8+n2*8+n3*4
        index,pool=cues+count*8,cues+count*12
        if pool>end:
            raise ValueError('Battle index exceeds bank')
        refs=defaultdict(list)
        for i in range(count):
            off=pool+struct.unpack_from('<I',raw,index+4*i)[0]
            if not pool<=off<end:
                raise ValueError('Battle pointer exceeds bank')
            refs[off].append(i)
        strings=[]
        pos=pool
        starts=set()
        while pos<end:
            stop=raw.find(b'\0',pos,end)
            if stop<0:
                raise ValueError('Unterminated battle string')
            starts.add(pos)
            if stop>pos:
                jp=raw[pos:stop].decode('cp932')
                strings.append({'offset':pos,'jp':jp,'index_entries':refs.get(pos,[])})
            pos=stop+1
        if not set(refs)<=starts:
            raise ValueError('Battle pointer is not a string start')
        blocks.append({'bank':bank,'base':base,'end':end,'pool':pool,'index':index,'count':count,'strings':strings})
    return blocks


def discover_table(raw,elf):
    candidates=[]
    for match in re.finditer(re.escape(struct.pack('>I',len(raw))),elf):
        last=match.start();start=last;value=len(raw)
        while start>=4:
            prev=struct.unpack_from('>I',elf,start-4)[0]
            if prev>=value or prev%16:
                break
            start-=4;value=prev
            if not value:
                break
        if value or last-start<8:
            continue
        table=list(struct.unpack_from('>%dI'%((last-start)//4+1),elf,start))
        try:
            blocks=parse_blocks(raw,table)
        except (ValueError,struct.error,UnicodeDecodeError):
            continue
        candidates.append((start,table,blocks))
    if len(candidates)!=1:
        raise ValueError('Battle bank table discovery is not unique')
    return candidates[0]


def extract():
    path=PKG/'DATA_REN/BTLC/SRVC.BIN';raw=path.read_bytes()
    elf_path=ROOT/'work/eboot/EBOOT.ELF';elf=elf_path.read_bytes()
    table_at,table,blocks=discover_table(raw,elf)
    rows=[];exclusions=[]
    def add(asset,sha,offset,jp,**extra):
        key=asset+':'+str(offset)
        rows.append(dict(id='battle_occ:'+digest(key.encode())[:20],asset=asset,asset_sha256=sha,
                         offset=offset,jp=jp,source_sha256=digest(jp.encode()),**extra))
    asset=path.relative_to(ROOT).as_posix();sha=digest(raw)
    for bank in blocks:
        for r in bank['strings']:
            if not r['index_entries'] and not r['jp'].startswith(('「','（','－')):
                exclusions.append(dict(asset=asset,bank=bank['bank'],**r,reason='Unreferenced malformed/truncated leftover pool data; no index points here.'))
                continue
            add(asset,sha,r['offset'],r['jp'],bank=bank['bank'],index_entries=r['index_entries'],
                binding='SRVC bank-local offset table' if r['index_entries'] else 'Intact unreferenced battle pool line')
    path=PKG/'COMMONDATA_REN/MTDATA/RPW_DATA.CPK';cpk=CPK(str(path))
    for member in cpk.files:
        raw=cpk.read(member);asset=path.relative_to(ROOT).as_posix()+':'+str(member['id'])
        for r in rpw_strings(raw):
            if r['ordinal'] in set(range(10,24))|{26,27,28,29}:
                add(asset,digest(raw),r['offset'],r['jp'],bank='RPW',ordinal=r['ordinal'],binding='RPW retreat quote')
    for relative,encoding,jp in scan_nul(elf[0x959c18:0x959f80]):
        add(elf_path.relative_to(ROOT).as_posix(),digest(elf),0x959c18+relative,jp,bank='ELF',binding='ELF retreat quote; consumer unverified')
    return {'schema':1,'scope':'Battle subtitles and retreat quotes included; story dialogue excluded.',
            'srvc_sha256':sha,'elf_sha256':digest(elf),'table_offset':table_at,'table':table,
            'banks':[{k:v for k,v in b.items() if k!='strings'} for b in blocks],'records':rows,'exclusions':exclusions,
            'limits':['No insertion, runtime layout, voice-cue interpretation or font verification.',
                      'Battle bank IDs are local to Rengoku. Never import sibling executable offsets or inferred speaker identities.']}


def seed(source):
    messages={}
    for r in source['records']:
        identity='battle:'+r['source_sha256'][:16]
        entry=messages.setdefault(identity,{'source':r['jp'],'source_sha256':r['source_sha256'],'occurrences':[],
                                           'text':None,'status':'untranslated'})
        assert entry['source']==r['jp']
        entry['occurrences'].append(r['id'])
    return {'schema':1,'language':'en','source_catalog_sha256':digest(encoded(source).encode()),'messages':messages}


def check_target(jp,text,glossary):
    expanded=validate_target(jp,text,glossary)
    if re.findall(r'\\[A-Za-z]',jp)!=re.findall(r'\\[A-Za-z]',expanded):
        raise ValueError('Battle line-break/control escapes changed')
    if jp.count('\n')!=expanded.count('\n'):
        raise ValueError('Battle literal newline count changed')
    if [jp.count(x) for x in '「」']!=[expanded.count(x) for x in '「」']:
        raise ValueError('Battle speech wrappers changed')
    return expanded


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command',choices=('extract','slice','apply','check','report'))
    ap.add_argument('proposal',nargs='?',type=Path)
    ap.add_argument('--start',type=int,default=0)
    ap.add_argument('--write',action='store_true')
    args=ap.parse_args()
    outputs={}
    if args.command=='extract':
        source=extract();locale=seed(source)
        print('Banks:',len(source['banks']),'table:',hex(source['table_offset']),'occurrences:',len(source['records']),
              'unique lines:',len(locale['messages']),'broken unreferenced remnants:',len(source['exclusions']))
        for r in source['records'][:5]:print(r['bank'],hex(r['offset']),r['jp'])
        if SOURCE.exists() or LOCALE.exists():raise ValueError('Existing battle catalog; refusing reseed')
        outputs={SOURCE:encoded(source),LOCALE:encoded(locale)}
    else:
        source=json.loads(SOURCE.read_bytes());locale=json.loads(LOCALE.read_bytes())
        if locale['source_catalog_sha256']!=digest(SOURCE.read_bytes()):raise ValueError('Battle source changed')
        glossary=localization.terms();items=list(locale['messages'].items())
        if args.command=='slice':
            subset=items[args.start:args.start+80];context=items[max(0,args.start-4):args.start+84]
            sources={r['id']:r for r in source['records']}
            corpus='\n'.join(v['source'] for _,v in context)
            brief={'source_catalog_sha256':locale['source_catalog_sha256'],'start':args.start,
                   'rows':[dict(id=k,**v,banks=sorted({str(sources[o]['bank']) for o in v['occurrences']})) for k,v in subset],
                   'adjacent_context':[{'id':k,'source':v['source'],'text':v['text']} for k,v in context if k not in dict(subset)],
                   'terms':[t for t in glossary if len(t['jp'])>=2 and t['jp'] in corpus],
                   'instructions':'Translate all rows, full meaning, no byte budget. Preserve literal backslash-n counts and 「」. Use $$Japanese$$ glossary references for named entities. Unknown speakers/gender stay uncertain. Read adjacent context. Report examined vs slice counts. Do not edit canonical or original assets.'}
            print(encoded(brief))
            outputs={ROOT/'work/battle_batches'/('%04d_brief.json'%args.start):encoded(brief)}
        elif args.command=='apply':
            proposal=json.loads(args.proposal.read_text(encoding='utf-8'))
            if proposal['source_catalog_sha256']!=locale['source_catalog_sha256']:raise ValueError('Stale battle proposal')
            for k,value in proposal['translations'].items():
                entry=locale['messages'][k]
                if value['source_sha256']!=entry['source_sha256']:raise ValueError('Stale battle line')
                check_target(entry['source'],value['text'],glossary)
                if entry['text'] and entry['text']!=value['text'] and value.get('previous')!=entry['text']:
                    raise ValueError('Existing translation requires exact previous-text guard: '+k)
                print(k,repr(entry['source']),'=>',repr(value['text']))
                entry.update(text=value['text'],status=value.get('status','draft'),batch=str(args.proposal),notes=value.get('notes',''))
            outputs={LOCALE:encoded(locale)}
        elif args.command=='check':
            fresh=extract()
            if fresh!=source:raise ValueError('Battle assets no longer match source')
            rows={r['id']:r for r in source['records']};seen=[]
            for k,v in items:
                if digest(v['source'].encode())!=v['source_sha256']:raise ValueError('Stale source')
                for occurrence in v['occurrences']:
                    if rows[occurrence]['jp']!=v['source']:raise ValueError('Wrong battle occurrence')
                    seen.append(occurrence)
                if v['text'] is not None:check_target(v['source'],v['text'],glossary)
                elif v['status']=='excluded_binary':
                    if BINARY_CANDIDATES.get(k)!=v['source']:raise ValueError('Unapproved battle exclusion')
                elif v['status']!='untranslated':raise ValueError('Missing battle translation')
            if Counter(seen)!=Counter(rows.keys()):raise ValueError('Battle occurrence coverage mismatch')
            print(Counter(v['status'] for _,v in items));print('All battle source bindings, glossary references and control markers pass.')
        elif args.command=='report':
            rows=['# Battle-line English draft','','Battle speech is included; story dialogue is excluded. No game insertion or runtime layout validation.','']
            pending=[];lengths=[]
            for k,v in items:
                if v['text']:
                    expanded=localization.expand(v['text'],glossary).replace('\\n','\n')
                    rows.extend(['## '+k,'',expanded,''])
                    lengths.extend(len(line) for line in expanded.splitlines())
                    if v['status']=='needs_review':
                        pending.append(dict(id=k,source=v['source'],text=v['text'],notes=v.get('notes','')))
                        rows.extend(['Review flag: '+v.get('notes','Unresolved context.'),''])
            included=[v for _,v in items if v['status']!='excluded_binary']
            report={'discovery_occurrences':len(source['records']),'discovery_entries':len(items),
                    'occurrences':sum(len(v['occurrences']) for v in included),'unique_lines':len(included),'banks':len(source['banks']),
                    'translated_entries':sum(bool(v['text']) for v in included),'excluded_binary_candidates':len(items)-len(included),
                    'unreferenced_malformed_remnants':len(source['exclusions']),
                    'statuses':dict(Counter(v['status'] for _,v in items)),'source_catalog_sha256':digest(SOURCE.read_bytes()),
                    'table_offset':source['table_offset'],'story_dialogue_changed':False,
                    'longest_expanded_english_line':max(lengths,default=0),
                    'length_note':'Character count is descriptive only; runtime font, wrap and screen bounds are unmeasured.'}
            status=['# Battle translation status','',
                '%d unique battle lines (%d stored occurrences) have English drafts. Story dialogue is excluded.' % (report['translated_entries'],report['occurrences']),'',
                'Read [the English battle lines](battle_lines_en.md). The canonical catalog is `localization/locales/en/battle_lines.json`; `analysis/battle_line_pending.json` records %d review flags.' % len(pending),'',
                '## Scope and extraction','',
                'The local SRVC contains 39 banks. Its offset table was discovered and structurally checked in Rengoku’s own decrypted executable at `0x952e80`; sibling executable offsets were not used. The catalog also includes RPW/executable retreat quotes. Intact unused battle lines and player-facing farewell lines in the battle banks remain included.','',
                'Thirty malformed, unreferenced pool remnants and two short ELF binary false positives are excluded. The immutable discovery catalog retains the two latter candidates for audit. All indexed pointers stay inside their bank and land at string starts.','',
                '## Review and terminology','',
                'Drafts and independent meaning proofs use 80-row slices plus neighboring context. Source/proposal hashes and exact previous-text guards bind corrections to the reviewed text. Meaning fixes precede scripted terminology normalization. See `analysis/battle_review_index.json`, `analysis/battle_terms.json` and `analysis/battle_terminology_applied.json`.','',
                'The inherited glossary remains unchanged. Local additions distinguish researched spellings, established project forms and provisional readings. Ambiguous omitted subjects, alien names, jokes and incantations retain explicit review notes. Original Japanese, quote wrappers, runtime tokens, literal backslash-n controls and actual retreat-quote newlines are preserved.','',
                '## Limits','',
                'This is translation source, not a playable patch. No insertion or runtime layout validation was performed. Voice-cue pairing and all speaker identities are not proven; numeric bank IDs alone are not identity evidence.','',
                'The longest expanded English line is %d characters. This is a descriptive count, not a verified screen budget. Font coverage, glyph widths, line wrapping, relocation and pointer consumers still need runtime work; full meaning was not shortened to fit source bytes.' % report['longest_expanded_english_line'],'',
                'The broader image/opaque-asset limits remain in [the non-dialogue coverage report](non_dialogue_status.md).','']
            print(encoded(report));outputs={ROOT/'docs/battle_lines_en.md':'\n'.join(rows),ROOT/'docs/battle_status.md':'\n'.join(status),ROOT/'analysis/battle_line_status.json':encoded(report),
                ROOT/'analysis/battle_line_pending.json':encoded({'entries':pending,'note':'English drafts exist; flags preserve meaning, identity and wording uncertainties.'})}
    if args.write:
        for path,body in outputs.items():
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body.encode())
    elif outputs:print('DRY RUN; --write saves only the previewed catalog/proposal/report files.')


if __name__=='__main__':main()
