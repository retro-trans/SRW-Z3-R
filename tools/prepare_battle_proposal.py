"""Bind an authored, at-most-80-line slice to immutable Japanese fingerprints."""
import argparse,json
from pathlib import Path
from battle_lines import ROOT,SOURCE,LOCALE,check_target
from non_dialogue import encoded,digest
import localization

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('authored',type=Path);ap.add_argument('--write',action='store_true');a=ap.parse_args()
    draft=json.loads(a.authored.read_text(encoding='utf-8'));locale=json.loads(LOCALE.read_bytes())
    if draft['source_catalog_sha256']!=digest(SOURCE.read_bytes()):raise ValueError('Stale authoring source')
    start=draft['start'];texts=draft['lines'];items=list(locale['messages'].items())
    if not 0<len(texts)<=80 or start<0 or start+len(texts)>len(items):raise ValueError('Invalid slice bounds')
    changes={}
    for (identity,entry),text in zip(items[start:start+len(texts)],texts):
        check_target(entry['source'],text,localization.terms())
        changes[identity]={'source_sha256':entry['source_sha256'],'text':text,'status':'draft','notes':''}
    context=items[max(0,start-4):start+len(texts)+4]
    report={'rows_in_slice':len(texts),'rows_examined':len(context),'adjacent_context_ids':[k for k,v in context if k not in changes],
            'identity_notes':'Banks 2/3: Firebug mercenary speech; identify from self-references, not a generic weapon-match guess.',
            'uncertainties':['Shared short lines can occur in other banks. Their generic wording avoids forcing a pilot identity.',
                             'No per-line cue interpretation or runtime layout measurement has been performed.']}
    out={'source_catalog_sha256':draft['source_catalog_sha256'],'translations':changes,'report':report}
    path=ROOT/'work/battle_batches'/('%04d.json'%start)
    print('Bound lines:',len(changes),'context examined:',len(context),'output',path)
    for k,v in list(changes.items())[:8]+list(changes.items())[-2:]:print(k,repr(v['text']))
    if a.write:path.write_bytes(encoded(out).encode())
    else:print('DRY RUN; --write saves the source-guarded proposal only.')

if __name__=='__main__':main()
