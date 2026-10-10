"""Preview the reviewed ending subject fix and missing keyword word gaps."""
import argparse,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

PREVIOUS="$$クロウ$$\n「It's fine. If Advent and the others do their part, this\n　Earth and that one should be able to travel between\n　each other」"
REPLACEMENT="$$クロウ$$\n「It's fine. If Advent and the others do their part,\n　travel between this Earth and the other one\n　should become possible」"


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    outputs={};changes=[];scanned=0
    for path in sorted((ROOT/'localization/locales/en').glob('STG*.json')):
        data=json.loads(path.read_text(encoding='utf8'));changed=False
        for identity,row in data['messages'].items():
            scanned+=1;old=row.get('text') or '';new=old
            if identity=='rengoku:STGZ3REN_00107:00045':
                if old not in (PREVIOUS,REPLACEMENT):raise ValueError('Ending review baseline changed')
                new=REPLACEMENT
            new=re.sub(r'(?<=[A-Za-z0-9])《',' 《',new)
            if old==new:continue
            row['text']=new
            row.setdefault('notes',[]).append('Build022: independently reviewed subject correction or keyword word spacing; source identity and wrappers preserved.')
            changes.append(dict(catalog=path.name,id=identity,previous=old,text=new));changed=True
        if changed:outputs[path]=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    print(json.dumps(changes,ensure_ascii=False,indent=2));print('WRITE' if args.write else 'DRY RUN',len(changes),'changes;',scanned,'records scanned')
    if args.write:
        for path,body in outputs.items():path.write_text(body,encoding='utf8')


if __name__=='__main__':main()
