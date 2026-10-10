"""Preview source-guarded Daimon and user-requested Asakim Dowin corrections."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    outputs, changes = {}, []
    for path in sorted((ROOT/'localization/locales/en').glob('*.json')):
        data = json.loads(path.read_text(encoding='utf8'))
        changed = False
        for identity, row in data.get('messages', {}).items():
            old = row.get('text') or ''
            source = row.get('source') or ''
            new = old
            if 'デイモーン' in source:
                new = re.sub(r'\bDemon\b', 'Daimon', new)
            if 'アサキム' in source or '$$アサキム$$' in old:
                new = re.sub(r'\bDowen\b', 'Dowin', new)
            if new == old:
                continue
            row['text'] = new
            changes.append({'catalog': path.relative_to(ROOT).as_posix(),
                            'id': identity, 'previous': old, 'text': new})
            changed = True
        if changed:
            outputs[path] = json.dumps(data, ensure_ascii=False, indent=2)+'\n'
    for rel, collection in [('localization/glossary_additions.json','terms'),
                            ('analysis/battle_terms.json','terms'),
                            ('analysis/characters.json','characters')]:
        path = ROOT/rel
        data = json.loads(path.read_text(encoding='utf8'))
        for row in data[collection]:
            if row['jp'] != 'アサキム・ドーウィン':
                continue
            if row['en'] != 'Asakim Dowin':
                changes.append({'catalog':rel,'jp':row['jp'],
                                'previous':row['en'],'text':'Asakim Dowin'})
            row['en'] = 'Asakim Dowin'
            note = ('Build021: user explicitly requests Asakim Dowin; overrides the '
                    'earlier wiki spelling. Bare Asakim and Japanese keyword links remain unchanged.')
            if collection == 'terms':
                row['status'] = 'project_style'
                row['note'] = note
            else:
                row['scope'] = 'Do not add background revelations to short combat calls. '+note
        outputs[path] = json.dumps(data, ensure_ascii=False, indent=2)+'\n'
    path = ROOT/'tools/normalize_battle_terms.py'
    old = path.read_text(encoding='utf8')
    new = old.replace("(('アサキム',),'Asakim Dowin','Asakim Dowen')",
                      "(('アサキム',),'Asakim Dowen','Asakim Dowin')")
    if old != new:
        changes.append({'catalog':path.relative_to(ROOT).as_posix(),
                        'previous':'Dowin -> Dowen','text':'Dowen -> Dowin'})
        outputs[path] = new
    report_path = ROOT/'analysis/battle_terminology_applied.json'
    report = json.loads(report_path.read_text(encoding='utf8'))
    report['do_not_touch']['アサキム・ドーウィン'] = 'Asakim Dowin'
    if report['do_not_touch'].get('デイモーン') != 'Daimon':
        changes.append({'catalog':'analysis/battle_terminology_applied.json',
                        'jp':'デイモーン','text':'Daimon (do-not-touch)'})
    report['do_not_touch']['デイモーン'] = 'Daimon'
    report.setdefault('category021_changes', []).extend(changes)
    outputs[report_path] = json.dumps(report, ensure_ascii=False, indent=2)+'\n'
    print(json.dumps(changes, ensure_ascii=False, indent=2))
    print('WRITE' if args.write else 'DRY RUN',len(changes),'changes')
    if args.write:
        for path, body in outputs.items():
            path.write_text(body, encoding='utf8')


if __name__ == '__main__':
    main()
