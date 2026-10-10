"""Preview missing spaces after dialogue keyword links; --write applies reviewed cases."""
import argparse,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 edits=[]
 for path in sorted((ROOT/'localization/locales/en').glob('STG*.json')):
  data=json.loads(path.read_text(encoding='utf8'));changed=False
  for key,row in data['messages'].items():
   old=row['text'];new=re.sub(r'》(?=[A-Za-z])','》 ',old)
   if key=='rengoku:STGZ3REN_00045:00052':
    new=new.replace('turned the\n　Earth','turned\n　the Earth')
   if new==old:continue
   edits.append({'id':key,'previous':old,'text':new});row['text']=new;changed=True
   row.setdefault('notes',[]).append('Build020: separate linked keyword from following English word; link order and identity preserved.')
  if changed and args.write:path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps(edits,ensure_ascii=False,indent=2));print('WRITE' if args.write else 'DRY RUN',len(edits),'records')
if __name__=='__main__':main()
