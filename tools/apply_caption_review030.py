"""Preview reviewed, source-bound caption wording; --write applies proposals."""
import argparse,json
from pathlib import Path
import battle_lines,localization

ROOT=Path(__file__).resolve().parents[1]
def main(paths,write):
    doc=localization.read(battle_lines.LOCALE);terms=localization.terms()
    changes=[];seen=set()
    for path in paths:
        review=localization.read(path)
        for row in review.get('proposals',review.get('corrections',[])):
            key=row['id'];assert key not in seen,'Repeated review ID';seen.add(key)
            current=doc['messages'][key];before=row.get('before',row.get('previous'));new=row['text']
            assert current['source_sha256']==row['source_sha256'],'Source fingerprint changed'
            assert current['source']==row['source'],'Japanese source changed'
            assert current['text'] in (before,new),'Reviewed English baseline changed'
            battle_lines.check_target(current['source'],new,terms)
            if current['text']==new:continue
            changes.append(dict(id=key,previous=current['text'],text=new,reason=row['reason']))
            current['text']=new
            note='2026-11-24 source/context review: concise full-meaning wording for two-row battle panel; controls and terminology preserved.'
            notes=current.get('notes')
            if isinstance(notes,list):notes.append(note)
            elif isinstance(notes,str):current['notes']=(notes+' '+note).strip()
            else:current['notes']=[note]
    print(localization.encoded(changes));print('Reviewed entries:',len(seen),'; canonical changes:',len(changes))
    if not write:print('DRY RUN: no canonical catalog changed.');return
    if changes:battle_lines.LOCALE.write_text(localization.encoded(doc),encoding='utf8')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('proposals',nargs='+',type=Path);p.add_argument('--write',action='store_true')
    a=p.parse_args();main(a.proposals,a.write)
