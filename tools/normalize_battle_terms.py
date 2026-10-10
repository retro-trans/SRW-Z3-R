"""Normalize researched names after battle meaning proof; originals/story files are untouched."""
import argparse
import json
import re
from non_dialogue import ROOT, encoded, digest, validate_target
from battle_lines import check_target
import localization

# Decisions newly verified during battle research. Longer alternatives go first.
VARIANTS=[
 (('沈黙の巨蟹',),'Silent Giant Crab','Taciturn Crab'),
 (('沈黙の巨蟹',),'Silent Crab','Taciturn Crab'),
 (('いがみ合う双子','いがみあう双子'),'The Feuding Twins','Quarreling Twins'),
 (('いがみ合う双子','いがみあう双子'),'Feuding Twins','Quarreling Twins'),
 (('いがみ合う双子','いがみあう双子'),'Quarrelling Twins','Quarreling Twins'),
 (('アサキム',),'Asakim Dowen','Asakim Dowin'),
 (('ブンマー・スパナ',),'Boomer Spanner','Bunmar Spanner'),
 (('ライアット・ジャレンチ',),'Riot Jarench','Riot Gia-Wrench'),
 (('ジャレンチ',),'Jarench','Gia-Wrench'),
]


def outside_refs(text,fn):
    return ''.join(part if i%2 else fn(part) for i,part in enumerate(re.split(r'(\$\$.*?\$\$)',text)))


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    glossary=localization.terms()
    terms=json.loads((ROOT/'analysis/battle_terms.json').read_bytes())['terms']
    decisions={t['jp']:t['en'] for t in terms}
    for t in glossary:
        if t['jp'] in decisions and decisions[t['jp']]!=t['en']:raise ValueError('Glossary conflict')
    proof=json.loads((ROOT/'analysis/battle_review_index.json').read_bytes())
    if proof['independently_reviewed_entries']!=3575:raise ValueError('Meaning proofreading incomplete')
    changes=[];note_changes=[];outputs={}
    for name in ('battle_lines','non_dialogue','artwork'):
        path=ROOT/'localization/locales/en'/(name+'.json');doc=json.loads(path.read_bytes())
        for identity,entry in doc['messages'].items():
            if not entry.get('text'):continue
            jp=re.sub(r'\s+','',entry['source'].replace('\\n',''))
            if 'ブンブン・スパナ' in jp and 'Boomer Spanner' in entry.get('notes',''):
                previous_note=entry['notes']
                entry['notes']=previous_note.replace('Boomer Spanner','Bunmar Spanner')
                note_changes.append({'catalog':path.relative_to(ROOT).as_posix(),'id':identity,
                    'source_sha256':entry['source_sha256'],'previous':previous_note,'notes':entry['notes']})
                print('NOTE',identity,repr(previous_note),'=>',repr(entry['notes']))
            def fix_variants(text):
                for guards,old,new in VARIANTS:
                    if any(g in jp for g in guards):
                        text=re.sub(r'(?<![A-Za-z])'+re.escape(old)+r'(?![A-Za-z])',lambda _:new,text)
                return text
            text=outside_refs(entry['text'],fix_variants)
            if name=='battle_lines':
                # A source guard prevents replacement of ordinary words with unrelated proper names.
                for term in sorted(terms,key=lambda t:len(t['en']),reverse=True):
                    if term['jp'] not in jp:continue
                    pattern=re.compile(r'(?<![A-Za-z])'+re.escape(term['en'])+r'(?![A-Za-z])')
                    text=outside_refs(text,lambda part:pattern.sub(lambda _:'$$'+term['jp']+'$$',part))
            if text==entry['text']:continue
            (check_target if name=='battle_lines' else validate_target)(entry['source'],text,glossary)
            changes.append({'catalog':path.relative_to(ROOT).as_posix(),'id':identity,
                            'source_sha256':entry['source_sha256'],'previous':entry['text'],'text':text})
            first=next((i for i,(a,b) in enumerate(zip(entry['text'],text)) if a!=b),0)
            start=max(0,first-65)
            print(name,identity,repr(entry['text'][start:first+150]),'=>',repr(text[start:first+150]))
            entry['text']=text;entry['terminology_review']='analysis/battle_terminology_applied.json'
        outputs[path]=encoded(doc)
    print('Name/reference changes:',len(changes))
    report_path=ROOT/'analysis/battle_terminology_applied.json'
    prior=json.loads(report_path.read_bytes()) if report_path.exists() else {}
    report={'changes':prior.get('changes',[])+changes,'note_changes':prior.get('note_changes',[])+note_changes,'do_not_touch':decisions,'meaning_review_index_sha256':digest((ROOT/'analysis/battle_review_index.json').read_bytes()),
            'note':'All independent meaning fixes preceded this name pass. Do not reapply stale drafting/proof proposals afterward.'}
    if args.write:
        for path,body in outputs.items():path.write_bytes(body.encode())
        report_path.write_bytes(encoded(report).encode())
    else:print('DRY RUN; --write applies only these source-guarded naming changes.')


if __name__=='__main__':main()
