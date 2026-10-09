"""Preview researched additions and explicitly guarded local spelling corrections."""
import argparse,json
from non_dialogue import ROOT,encoded,digest
import localization

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    path=ROOT/'localization/glossary_additions.json';doc=json.loads(path.read_text(encoding='utf-8'))
    glossary=localization.terms()
    added=[]
    for term in json.loads((ROOT/'analysis/battle_terms.json').read_text(encoding='utf-8'))['terms']:
        old=[t for t in glossary if t['jp']==term['jp']]
        if old:
            if {t['en'] for t in old}=={term['en']}:continue
            if len(old)!=1 or term.get('override_from')!=old[0]['en']:
                raise ValueError('Explicit override required: '+term['jp'])
        identity=old[0]['id'] if old else 'battle_glossary:'+digest(term['jp'].encode())[:16]
        existing=[t for t in doc['terms'] if t['id']==identity]
        new=dict(term,id=identity,source='Battle terminology research')
        if existing:
            if len(existing)!=1 or existing[0]['en']!=term.get('override_from'):
                raise ValueError('Existing overlay needs guarded migration: '+term['jp'])
            # These battle entries are local additions. Do not mislabel a local
            # spelling migration as an override of an imported base entry.
            new.pop('override_from',None)
            new['previous_local_spelling']=existing[0]['en']
            doc['terms'][doc['terms'].index(existing[0])]=new
            print(term['jp'],existing[0]['en'],'=>',term['en'],'(guarded local correction)')
            continue
        added.append(new);print(term['jp'],'=>',term['en'],term['status'])
    print('New terms:',len(added))
    if args.write:
        doc['terms'].extend(added);doc['verified_on']='2026-09-25';path.write_text(encoded(doc),encoding='utf-8')
    else:print('DRY RUN; --write adds only these terms.')

if __name__=='__main__':main()
