"""Add source-grounded Rengoku library profiles without changing dialogue."""
import argparse
import json
from non_dialogue import ROOT, SOURCE, LOCALE, digest, encoded

# Root-authored summaries of the corresponding library entries. Unknown means
# the consulted source did not establish gender, never an inference from a name.
PROFILES={
  1:('female','Glory Star second lieutenant','Earnest, conscientious and determined; formerly timid and struggling with despair.',None),
  2:('male','Beater Service repairer','Generous, boisterous and hot-blooded; prone to extreme anger.','The Heat; The Crusher'),
  3:('female','Beater Service business manager and Gunleon co-pilot','Strong-willed and playful; keeps a diary and calls herself Rand\'s fiancée.',None),
  4:('male','Scott Lab Dimensional Beast Buster; former Firebug member','A sincere fighter beneath a cynical rogue persona that repeatedly gives way to comedy.',None),
  5:('female','Head of Scott Lab; robotics, energy and space-time researcher','Prioritizes research, with unconventional habits and interests.',None),
  7:('female','Chrono Reformist support and medical specialist','Gentle, obedient and devoted to supporting Advent.',None),
  8:('unknown','Chrono Reformist combatant','Taciturn and obedient to Advent.',None),
  9:('unknown','Chrono Reformist mechanic and support member','Honest, unassuming and deeply loyal to Advent.',None),
  10:('female','Junior Sidereal Sphere researcher','Timid and self-critical, but unexpectedly determined once committed to a decision.',None),
  12:('male','Sidereal deserter; later revealed as Antares deputy commander','Easygoing and well-educated, concealing a calculating nature.',None),
  13:('male','Mysterious boy rescued by the protagonists','Cynical, hostile and reluctant to reveal his past.','Orion is the name Setsuko gives him.'),
  14:('unknown','Sidereal commander; later identified as leader of Antares','Conceited and theatrical; calls himself a master strategist but plans poorly and struggles with surprises.',None),
  15:('male','Sidereal executive and Sphere Reactor','Taciturn, unemotional and executioner-like.',None),
  16:('male','Commander of Geminis','A powerful psychic given to idleness and drinking; marked by anger and despair.',None),
  17:('female','Deputy commander of Geminis','Calm, capable and ruthless.',None)
}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write',action='store_true')
    args=ap.parse_args()
    source=json.loads(SOURCE.read_bytes())
    messages=json.loads(LOCALE.read_text(encoding='utf-8'))['messages']
    path=ROOT/'analysis/characters.json'
    doc=json.loads(path.read_text(encoding='utf-8'))
    existing={r['jp'] for r in doc['characters']}
    for number,(gender,position,personality,nickname) in PROFILES.items():
        rows=[r for r in source['records'] if r.get('family')=='PT' and r.get('entry')==number]
        fields={r['locator']:r for r in rows}
        jp=fields['CHFN']['jp']
        if jp in existing:
            continue
        en=messages['library:'+digest(jp.encode())[:16]]['text']
        item={'jp':jp,'en':en,'nickname':nickname,'gender':gender,'position':position,'personality':personality,
              'sources':['source/non_dialogue.json#'+fields[tag]['id'] for tag in ('CHFN','CHNN','DSCR','DSC2')],
              'source_guards':{fields[tag]['id']:fields[tag]['source_sha256'] for tag in ('CHFN','CHNN','DSCR','DSC2')},
              'name_reference':'analysis/rengoku_terms.json and inherited analysis/base_provenance.json',
              'scope':'Rengoku library characterization, including later revelations where stated; do not insert these facts into dialogue.',
              'gender_note':'Unknown when not established by the consulted profile; never inferred from the name.'}
        doc['characters'].append(item)
        print(jp,'->',en,'/',gender,'/',position)
    doc['verified_on']='2026-09-25'
    if args.write:
        path.write_text(encoded(doc),encoding='utf-8')
    else:
        print('DRY RUN; --write adds these profiles.')


if __name__=='__main__':
    main()
