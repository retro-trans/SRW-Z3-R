"""Read-only compiled proof: original cues, bounded Japanese, full owned English."""
import argparse,json,struct
from pathlib import Path
import localization
from rengoku_runtime import TEXT,WIDTHS,require,sha
from cpk import CPK
import rengoku_battle_subtitles as layout

ROOT=Path(__file__).resolve().parents[1]

def check(build):
    build=Path(build);report=json.loads((build/'BUILD_REPORT.json').read_text(encoding='utf8'))
    elf=(build/'intermediate/EBOOT.ELF').read_bytes()
    require(sha(elf)==report['self']['elf_payload_sha256'],'Compiled executable identity changed')
    class Codec:
        codes={c:int(v['cp932'],16) for c,v in report['font_mapping'].items()}
        widths={i:w for i,w in enumerate(elf[WIDTHS-0x10000:WIDTHS-0x10000+4480])}
        def encode(self,text):
            return b''.join(struct.pack('>H',self.codes[c]) if c in self.codes else c.encode('cp932') for c in text)
    codec=Codec()
    def string(va):
        p=va-0x10000;require(0<=p<len(elf),'Draw lookup outside compiled ELF')
        return elf[p:elf.index(b'\0',p)]
    def lookup(key):
        bucket=int.from_bytes(key[:2],'big');p=struct.unpack_from('>I',elf,TEXT-0x10000+bucket*4)[0]
        while p:
            src,dst=struct.unpack_from('>II',elf,p-0x10000)
            if not src:break
            if string(src)==key:return string(dst),dst
            p+=8
        raise ValueError('Missing compiled battle caption')
    target=build/'RPCS3/NPJB00689/USRDIR/DATA_REN/BTLC/SRVC.BIN'
    original=ROOT/'work/pkg/USRDIR/DATA_REN/BTLC/SRVC.BIN'
    require(target.read_bytes()==original.read_bytes(),'Native battle cues or metadata changed')
    source=json.loads((ROOT/'source/battle_lines.json').read_text(encoding='utf8'))
    locale=json.loads((ROOT/'localization/locales/en/battle_lines.json').read_text(encoding='utf8'))
    terms=localization.terms();byid={oid:r for r in locale['messages'].values() for oid in r['occurrences']}
    checked=0;unique=set();maximum=0
    for r in source['records']:
        if not isinstance(r['bank'],int):continue
        key=r['jp'].replace('\\n','\n').encode('cp932');maximum=max(maximum,len(key)+1)
        require(len(key)+1<=134,'Original caption would overwrite native state')
        en=localization.expand(byid[r['id']]['text'],terms)
        display,reason=layout.fit(codec,en);require(reason is None,'Caption still exceeds panel: '+r['id'])
        data,address=lookup(key)
        require(address>=TEXT and data==codec.encode(display.replace('\\n','\n')),
                'Owned compiled caption differs: '+r['id'])
        checked+=1;unique.add(key)
    stage=next(p/'rebuilt.cpk' for p in (build/'intermediate').glob('archive_*') if (p/'STGZ3REN.SDAT').exists())
    archive=CPK(str(stage));scene=archive.read(next(e for e in archive.files if e['id']==15)).replace(b'\r\n',b'\n')
    story=json.loads((ROOT/'localization/locales/en/STGZ3REN_00015.json').read_text(encoding='utf8'))
    for suffix in ('00015','00025','00036'):
        identity='rengoku:STGZ3REN_00015:'+suffix
        text=localization.expand(story['messages'][identity]['text'],terms)
        require(codec.encode(text) in scene,'Compiled honorific correction missing: '+identity)
    proof=dict(version=report['version'],original_srvc_and_all_6356_cues_preserved=True,
        compiled_caption_occurrences_checked=checked,unique_converted_draw_keys=len(unique),
        largest_native_caption_bytes=maximum,native_capacity=134,
        all_english_in_owned_draw_storage=True,all_captions_fit_two_rows=True,
        compiled_honorific_corrections_checked=3,
        gameplay_tested=False,all_passed=True)
    print(json.dumps(proof,indent=2));return proof

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('build',type=Path)
    check(p.parse_args().build)
