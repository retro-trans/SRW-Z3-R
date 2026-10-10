"""Preview canonical skill/bonus fixes and lossless story reflow; --write opts in."""
import argparse
import json
import re
from pathlib import Path
from build_game import Build, ROOT, document
from rengoku_runtime import DEFAULT_FONT, require
from rengoku_screenshot_layout import line_width
import localization

FIXES={
 'gameplay:515dc6f0f7ab972a': 'End your phase without acting: Zeal + Accel.\nAll main pilots on your team regain 5 SP.\nNo effect when held by the sub-unit.',
 'gameplay:e185759240aba50f': 'End your phase without acting: Zeal + Accel.\nAll main pilots on your team regain 5 SP.\nNo effect when held by the sub-unit.',
 'interface:e9f6530cad498ede': 'Weapon range +1, except MAP and range-1 weapons.',
 'interface:f446f2b2a924528c': 'Weapon range +1, except MAP and range-1 weapons.',
 'interface:46fa24306e542f69': 'Song range +1, except MAP songs and range-1 songs.',
}
SKILLS={
 'カウンター': "May counter first; chance depends on skill level and the Skill stat difference. No effect when held by the team's sub-unit.",
 'ネゴシエイター': "After battle, the foe's Focus -3. No repair costs if this pilot is deployed when those costs are calculated.",
 '物質転送': 'Once per map, Material Transfer lets this unit use a Repair Kit, Propellant Tank or Cartridge on itself.',
 'プレッシャー': 'Deal more and take less damage vs. lower Skill. Effect grows with skill level. Range: skill level x 2 squares.',
}
STORY='rengoku:STGZ3REN_00028:00020'
STORY_TEXT="$$アドヴェント$$\n「As expected of the team with Area 35's ace, the\n　wandering repairman and the money-minded expert\n　mercenary. They gladly agreed to help us」"
STORY_FIXES={
 STORY:STORY_TEXT,
 'rengoku:STGZ3REN_00034:00063':"$$サルディアス$$\n「As your new comrade-in-arms, I'd like a name too.\n　Unfortunately, I'm rather fond of the name\n　$$サルディアス$$...」",
 'rengoku:STGZ3REN_00046:00080':'$$クロウ$$\n「Turns out the $$次元転移砲$$ runs on\n　《$$次元力$$》. Adjust it, and it can heal\n　and resupply instead of attacking」',
 'rengoku:STGZ3REN_00092:00010':"$$クロウ$$\n「People on this Earth have looked out for us.\n　Above all, I can't stand guys who mess with someone\n　else's planet just to suit themselves」",
}


def reflow(text, codec, glossary):
    name,sep,body=text.partition('\n')
    require(sep,'Missing speaker')
    words=re.findall(r'(?:\$\$.*?\$\$|《.*?》|[^\s])+',body.replace('\n　',' '))
    lines=[];line=''
    for word in words:
        trial=(line+' '+word).strip()
        prefix='' if not lines else '　'
        if line and line_width(codec,localization.expand(prefix+trial,glossary),32)>870:
            lines.append(line);line=word
        else:line=trial
    if line:lines.append(line)
    target=name+'\n'+lines[0]+''.join('\n　'+s for s in lines[1:])
    require(target.partition('\n')[2].split()==body.split(),'Story words changed')
    return target,len(lines)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    b=Build(DEFAULT_FONT);path=ROOT/'localization/locales/en/non_dialogue.json'
    nd=json.loads(path.read_text(encoding='utf8'));by={r['id']:r for r in b.source['records']}
    pending=json.loads((ROOT/'work/skill019_pending.json').read_text(encoding='utf8'))
    for r in pending:
        if r['family']=='sk-pri' and r['name'] in SKILLS:
            FIXES[by[r['occurrence']]['group']+':'+by[r['occurrence']]['source_sha256'][:16]]=SKILLS[r['name']]
    changes=[];writes={}
    for identity,target in FIXES.items():
        entry=nd['messages'][identity]
        if entry['text']==target:continue
        ndresult=__import__('non_dialogue').validate_target(entry['source'],target,b.glossary)
        changes.append({'id':identity,'old':entry['text'],'new':target,'category':'skill/bonus'})
        entry['text']=target
        note='Build019: source-reviewed wording for measured panel bounds.'
        if isinstance(entry.get('notes'),str):entry['notes'] += ' '+note
        else:entry.setdefault('notes',[]).append(note)
    writes[path]=nd
    unresolved=[];examined=0;slices=[]
    for path in sorted((ROOT/'localization/locales/en').glob('STG*.json')):
        data=json.loads(path.read_text(encoding='utf8'));items=list(data['messages'].items());blocks=set();changed=False
        for index,(identity,entry) in enumerate(items):
            text=entry.get('text')
            if not text or not b.story_rows[identity]['pid']:continue
            expanded=localization.expand(text,b.glossary)
            if identity not in STORY_FIXES and max(line_width(b.codec,s,32) for s in expanded.split('\n')[1:])<=870:continue
            blocks.add(index//80)
            target,count=(STORY_FIXES[identity],3) if identity in STORY_FIXES else reflow(text,b.codec,b.glossary)
            if count>3:
                unresolved.append({'id':identity,'needed_lines':count,'text':text,'suggested_reflow':target});continue
            errors,_=localization.validate(b.story_rows[identity],dict(entry,text=target),b.glossary)
            require(not errors,str(errors))
            require(max(line_width(b.codec,s,32) for s in localization.expand(target,b.glossary).split('\n')[1:])<=870,'Story line still exceeds panel')
            changes.append({'id':identity,'old':text,'new':target,'category':'story'});entry['text']=target
            entry.setdefault('notes',[]).append('Build019: measured dialogue reflow; speaker, wrappers, links and word order preserved.' if identity not in STORY_FIXES else 'Build019: source-reviewed concise dialogue preserving meaning and terminology.')
            changed=True
        if changed:writes[path]=data
        for block in blocks:
            lo=block*80;hi=min(len(items),lo+80);exlo=max(0,lo-5);exhi=min(len(items),hi+5)
            examined+=exhi-exlo;slices.append({'member':path.stem,'start':lo,'in_slice':hi-lo,'examined':exhi-exlo})
    report={'changes':changes,'pending':unresolved,'slices':slices,'records_examined_including_context':examined}
    (ROOT/'work/category019_preview.json').write_text(document(report),encoding='utf8')
    print(document(report))
    if args.write:
        for path,data in writes.items():path.write_text(document(data),encoding='utf8')
        print('Applied inspected canonical changes.')
    else:print('DRY RUN: canonical files unchanged.')


if __name__=='__main__':main()
