"""Read-only proof of compiled objective lookups and Elgan's story spelling."""
import argparse
import json
from pathlib import Path
import struct
from cpk import CPK
from rengoku_runtime import TEXT,require,sha


def check(build):
    build=Path(build)
    report=json.loads((build/'BUILD_REPORT.json').read_text(encoding='utf8'))
    elf=(build/'intermediate/EBOOT.ELF').read_bytes()
    require(sha(elf)==report['self']['elf_payload_sha256'],'Compiled ELF identity changed')
    def encode(text):
        return b''.join(bytes.fromhex(report['font_mapping'][c]['cp932'])
                       if c in report['font_mapping'] else c.encode('cp932') for c in text)
    def string(address):
        p=address-0x10000
        require(0<=p<len(elf),'Lookup pointer outside compiled ELF')
        return elf[p:elf.index(b'\0',p)]
    checks=0
    for row in report['operation_layout']:
        for fragment in row['formatted']:
            key=fragment['source'].encode('cp932')
            bucket=int.from_bytes(key[:2],'big')
            entry=struct.unpack_from('>I',elf,TEXT-0x10000+bucket*4)[0]
            found=None
            while entry:
                source,target=struct.unpack_from('>II',elf,entry-0x10000)
                if not source:break
                if string(source)==key:
                    found=string(target);break
                entry+=8
            require(found==encode(fragment['display']),'Compiled operation lookup differs: '+fragment['source'])
            checks+=1
    stage=next(p/'rebuilt.cpk' for p in (build/'intermediate').glob('archive_*')
               if (p/'STGZ3REN.SDAT').exists())
    c=CPK(str(stage));scene=c.read(next(e for e in c.files if e['id']==4))
    require(encode('Roddick') in scene,'Compiled opening scene is missing Roddick')
    require(encode('Rhodic') not in scene,'Compiled opening scene still contains Rhodic')
    print(json.dumps(dict(version=report['version'],operation_occurrences=len(report['operation_layout']),
        compiled_formatted_lookup_checks=checks,all_passed=True,
        compiled_STG00004_contains_Roddick=True,compiled_STG00004_contains_Rhodic=False,
        gameplay_tested=False),indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('build',type=Path)
    check(ap.parse_args().build)
