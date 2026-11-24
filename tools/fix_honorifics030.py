"""Preview source-reviewed titles before permission to omit them; --write applies."""
import argparse
from pathlib import Path
import localization

ROOT=Path(__file__).resolve().parents[1]
ROWS={
 '00015':('9a3bc821fd',
  "$$セツコ$$\n「I'll be coming along with you.\n　Thank you for having me, $$アドヴェント$$,\n　$$ブルー$$」",
  "$$セツコ$$\n「I'll be coming along with you.\n　Thank you for having me, Mr. $$アドヴェント$$,\n　Mr. $$ブルー$$」"),
 '00025':('2eb81ff61b',
  '$$セツコ$$\n「Now that I think of it, you did say you and the others\n　crossed over the dimensional barrier, $$ブルー$$...」',
  '$$セツコ$$\n「Now that I think of it, you did say you and the others\n　crossed over the dimensional barrier, Mr. $$ブルー$$...」'),
 '00036':('42093de82f','$$セツコ$$\n「Likewise, $$ブルー$$」',
  '$$セツコ$$\n「Likewise, Mr. $$ブルー$$」')}

def main(write):
    path=ROOT/'localization/locales/en/STGZ3REN_00015.json'
    doc=localization.read(path)
    source=localization.read(ROOT/'source/story/STGZ3REN_00015.json')
    byid={r['id']:r for r in source['records']};changed=[]
    for suffix,(fingerprint,old,new) in ROWS.items():
        identity='rengoku:STGZ3REN_00015:'+suffix;row=byid[identity];entry=doc['messages'][identity]
        assert entry['source_sha']==fingerprint,identity
        assert entry['text'] in (old,new),'Reviewed English baseline changed'
        previous=entry['text'];entry['text']=new
        errors,_=localization.validate(row,entry,localization.terms());assert not errors,errors
        if previous!=new:
            changed.append(dict(id=identity,previous=previous,text=new))
            entry.setdefault('notes',[]).append('2026-11-24 context review: retain Mr. until Advent/Blue explicitly permits bare-name address.')
    print(localization.encoded(changed));print('Canonical changes:',len(changed))
    if not write:print('DRY RUN: --write applies the three reviewed honorific corrections.');return
    if changed:path.write_text(localization.encoded(doc),encoding='utf8')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true')
    main(p.parse_args().write)
