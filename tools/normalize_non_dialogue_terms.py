"""Apply reviewed terminology after meaning proof; preview each changed target."""
import argparse
import json
import re
from non_dialogue import ROOT, LOCALE, SOURCE, digest, encoded
import localization


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write',action='store_true')
    args=ap.parse_args()
    config=json.loads((ROOT/'analysis/rengoku_terms.json').read_text(encoding='utf-8'))
    glossary=localization.terms()
    overlay_path=ROOT/'localization/glossary_additions.json'
    overlay=json.loads(overlay_path.read_text(encoding='utf-8'))
    overlay_ids={t['id'] for t in overlay['terms']}
    added=[]
    for jp,en,kind,source,status,variants in config['terms']:
        old=[t for t in glossary if t['jp']==jp]
        if old and {t['en'] for t in old}=={en}:
            continue
        if len(old)>1:
            raise ValueError('Ambiguous glossary term: '+jp)
        t={'id':old[0]['id'] if old else 'rengoku_glossary:'+digest(jp.encode())[:16],
           'jp':jp,'en':en,'kind':kind,'status':status,'source':'オリジナル',
           'src':config['sources'].get(source,source),'note':'Decision and variants: analysis/rengoku_terms.json.'}
        if old:
            t['override_from']=old[0]['en']
        if t['id'] in overlay_ids:
            raise ValueError('Existing overlay needs explicit migration: '+jp)
        overlay['terms'].append(t)
        added.append(t)
    rules=[]
    for jp,en,kind,source,status,variants in config['terms']:
        for variant in variants:
            rules.append((jp,re.compile(r'(?<![A-Za-z])'+re.escape(variant)+r'(?![A-Za-z])'),en))
    # Exact source guards avoid conflating a Spirit icon, scan command, or person
    # with ordinary English words and user-interface mail settings.
    def normalize(jp,text):
        title=config.get('chapter_titles',{}).get(jp.strip())
        if title:
            return text.replace(text.strip(),title)
        for guard,pattern,replacement in sorted(rules,key=lambda r:len(r[1].pattern),reverse=True):
            if guard in jp or guard=='幸運' and jp=='幸':
                text=pattern.sub(replacement,text)
        return text
    changes=[]
    outputs=[]
    for path in (LOCALE,LOCALE.with_name('artwork.json')):
        doc=json.loads(path.read_text(encoding='utf-8'))
        for identity,entry in doc['messages'].items():
            if not entry.get('text'):
                continue
            previous=entry['text']
            text=normalize(entry['source'],previous)
            if text!=previous:
                print(identity,repr(previous[:140]),'->',repr(text[:140]))
                entry['text']=text
                entry['terminology_review']='analysis/non_dialogue_terminology_applied.json'
                changes.append({'catalog':path.relative_to(ROOT).as_posix(),'id':identity,'source_sha256':entry['source_sha256'],'previous':previous,'text':text})
        outputs.append((path,doc))
    # One Japanese label has both command and statistic consumers.
    doc=outputs[0][1]
    report=json.loads((ROOT/'work/non_dialogue_reviews/secondary_03.json').read_text(encoding='utf-8'))
    stat_ids=['nd:1afc01fdd44da4c61d1c','nd:31f736e81c56503bb57e','nd:22c2ce963408603182b2','nd:dc87b3d43e5bbd233423',
              'nd:945b0273fc2f703da00a','nd:47a20d60159d5921e3c1','nd:7c7bb741dcbec572c1c1','nd:daafcbf75255805713bb']
    entry=doc['messages']['menu_resource:75ba7a572706c98e']
    if entry['source']!='防御' or not set(stat_ids)<=set(entry['occurrences']):
        raise ValueError('Defense occurrence guards changed')
    for identity in stat_ids:
        entry.setdefault('occurrence_overrides',{})[identity]={'text':'Defense','reason':'Pilot statistic, not battle action; secondary_03 proof and exact_sync_final context.'}
    print('Glossary additions/overrides:',len(added),'target changes:',len(changes),'Defense occurrence overrides:',len(stat_ids))
    for t in added:
        print(t['jp'],'->',t['en'],t['status'])
    if args.write:
        overlay['verified_on']='2026-09-25'
        overlay_path.write_text(encoded(overlay),encoding='utf-8')
        for path,doc in outputs:
            path.write_text(encoded(doc),encoding='utf-8')
        output={'source_catalog_sha256':digest(SOURCE.read_bytes()),'changes':changes,'glossary_updates':added,'occurrence_overrides':stat_ids,
                'do_not_touch':[t[1] for t in config['terms']], 'note':'Meaning proofreading applied first. Dialogue files and base snapshot were not edited.'}
        audit_path=ROOT/'analysis/non_dialogue_terminology_applied.json'
        if audit_path.exists():
            previous=json.loads(audit_path.read_text(encoding='utf-8'))
            output['changes']=previous['changes']+changes
            output['glossary_updates']=previous['glossary_updates']+added
        audit_path.write_text(encoded(output),encoding='utf-8')
    else:
        print('DRY RUN; --write applies terminology and adds guarded occurrence overrides.')


if __name__=='__main__':
    main()
