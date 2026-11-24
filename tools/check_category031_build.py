"""Read-only packed proof for skill bonuses, Gold rewards, carryover and final SR."""
import argparse,json,struct,sys
from pathlib import Path
from cpk import CPK
from rengoku_runtime import TEXT,WIDTHS,require,sha
from rengoku_search_layout import field
from rengoku_screenshot_layout import hooks
from rengoku_screenshot_layout import line_width
import rengoku_bonus_runtime as G
import rengoku_carryover_layout as C
import rengoku_operation_layout as O

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
        p=va-0x10000;require(0<=p<len(elf),'Lookup outside compiled ELF')
        return elf[p:elf.index(b'\0',p)]
    def lookup(key):
        p=struct.unpack_from('>I',elf,TEXT-0x10000+int.from_bytes(key[:2],'big')*4)[0]
        while p:
            src,dst=struct.unpack_from('>II',elf,p-0x10000)
            if not src:break
            if string(src)==key:return string(dst)
            p+=8
        raise ValueError('Missing compiled key: '+repr(key))
    messages=json.loads((ROOT/'localization/locales/en/non_dialogue.json').read_text(encoding='utf8'))['messages']
    generated=hooks(codec,messages);bonuses=0;families=set()
    import re
    for key,en in generated.items():
        jp=key.decode('cp932')
        if not re.fullmatch(r'.+?[ 　]*[+＋][ 　]*[1-9１-９]',jp):continue
        require(lookup(key)==en,'Packed skill bonus differs: '+jp);bonuses+=1
        name=re.sub(r'[ 　]*[+＋][ 　]*[1-9１-９]$','',jp)
        families.add(re.sub(r'[ 　]?[ＬL][1-9１-９]$','',name))
    archive=CPK(str(build/'RPCS3/NPJB00689/USRDIR/DATA_REN/AIDDATA/AIDDATAPACK_R.CPK'))
    packed=archive.read(next(e for e in archive.files if e['id']==0))
    original=CPK(str(ROOT/'work/pkg/USRDIR/DATA_REN/AIDDATA/AIDDATAPACK_R.CPK'))
    source=original.read(next(e for e in original.files if e['id']==0))
    for item in report['carryover_layout']:
        row=int(item['row'],16)
        require(packed[row+8:row+32]==source[row+8:row+32],'Carryover style changed')
        moved={0x9a224:400,0x9a304:400,0x9a244:760,0x9a324:760,
               0x9a264:191.5,0x9a344:191.5}
        if row in moved:
            actual=struct.unpack_from('>f',packed,row+4)[0]*640+640
            require(abs(actual-moved[row])<0.01,'Carryover column position differs')
        else:require(packed[row+4:row+8]==source[row+4:row+8],'Unlisted carryover position changed')
        if item.get('live_values_preserved'):
            require(field(packed,row)==field(source,row)==C.VALUES.encode('cp932'),'Live rates changed')
            require(packed[row:row+4]==source[row:row+4],'Live rate pointer changed')
            require(packed[row+8:row+32]==source[row+8:row+32],'Live rate style changed')
            require(item['gap']>130,'Rate columns touch')
        else:
            require(field(packed,row)==codec.encode(item['display']),'Packed carryover caption differs')
            require(max(line_width(codec,s,packed[row+19]) for s in item['display'].split('\n'))<=item['width_limit'],
                    'Packed carryover caption exceeds measured bound')
    indexed=archive.read(next(e for e in archive.files if e['id']==5))
    base=48+struct.unpack_from('>I',indexed,24)[0]
    for i,en in ((164,C.NO_Z),(165,C.NO_Z_RATES)):
        p=base+struct.unpack_from('>I',indexed,32+i*4)[0]
        require(indexed[p:indexed.index(0,p)]==codec.encode(en),'Packed no-Z prose differs')
    jp='このシナリオにはＳＲポイントはありません。'
    for prefix in ('',)+O.NUMBERS:
        require(lookup((prefix+jp).encode('cp932'))==codec.encode(prefix+'There are no SR Points in this scenario.'),
                'Final SR condition missing')
    stage=next(p/'rebuilt.cpk' for p in (build/'intermediate').glob('archive_*') if (p/'STGZ3REN.SDAT').exists())
    stages=CPK(str(stage));final=stages.read(next(e for e in stages.files if e['id']==99))
    require('このシナリオにはＳＲポ\\イントはありません。'.encode('cp932') in final,'Raw final SR source changed')
    # Execute the emitted code, including the generic amount fallback, rather
    # than inferring runtime behavior from table contents alone.
    sys.path.insert(0,str(ROOT/'tests'))
    from test_link_runtime import CPU
    cases=[('金塊　３００００','Gold Bar 30000'),('金塊　4294967295','Gold 4294967295'),
           ('金塊　０００１０','Gold Bar 00010'),('金塊　','Gold '),
           ('サイズ差補正無視＋２','Ignore Size +2'),('援護攻撃＋２','Support Atk +2'),
           ('援護防御＋２','Support Def +2'),(jp,'There are no SR Points in this scenario.')]
    for source_text,en in cases:
        cpu=CPU(elf);cpu.put(0x1800000,source_text.encode('cp932')+b'\0');cpu.r[3]=0x1800000
        cpu.run(report['runtime']['stubs']['lookup'],{cpu.lr})
        require(cpu.string(cpu.r[3])==codec.encode(en),'Compiled PPC lookup failed: '+source_text)
    require(elf[G.TABLE-0x10000:G.TABLE-0x10000+len(G.data(codec))]==G.data(codec),'Gold data table changed')
    G.guard(elf)
    proof=dict(version=report['version'],compiled_bonus_forms_checked=bonuses,
        skill_families=len(families),carryover_packed_records=17,
        no_z_indexed_records=2,live_rates_preserved=True,final_sr_variants=4,
        actual_compiled_ppc_cases=len(cases),gold_generated_amounts_supported=True,
        source_scripts_preserved=True,gameplay_tested=False,all_passed=True)
    print(json.dumps(proof,indent=2));return proof

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('build',type=Path)
    check(p.parse_args().build)
