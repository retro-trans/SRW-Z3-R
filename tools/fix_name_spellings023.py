"""Apply the user's Bluest/Roddick spellings; preview before --write."""
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
import localization

ROOT = Path(__file__).resolve().parents[1]
NAMES = {'クロウ・ブルースト': 'Crowe Bluest', 'ブルースト': 'Bluest',
         'エルガン・ローディック': 'Elgan Roddick', 'ローディック': 'Roddick'}
NOTE = ('User spelling correction, 2026-10-10: Crowe Bluest and Elgan Roddick, '
        'including surname aliases. Overrides earlier inherited/wiki choices; '
        'Japanese identities and keyword links remain unchanged.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    outputs, changes = {}, []

    def read(relative):
        path = ROOT / relative
        return path, json.loads(path.read_text(encoding='utf8'))

    def save(path, previous, data):
        if previous != data:
            outputs[path] = json.dumps(data, ensure_ascii=False, indent=2) + '\n'

    path, overlay = read('localization/glossary_additions.json')
    previous = copy.deepcopy(overlay)
    inherited = {t['jp']: t for t in localization.terms()}
    for jp, en in NAMES.items():
        matches = [t for t in overlay['terms'] if t['jp'] == jp]
        if len(matches) > 1:
            raise ValueError('Ambiguous overlay: ' + jp)
        if matches:
            term = matches[0]
        else:
            base = inherited.get(jp)
            term = {'id': base['id'] if base else 'rengoku_glossary:' + hashlib.sha256(jp.encode()).hexdigest()[:16],
                    'jp': jp, 'kind': 'pilot' if 'ブルースト' in jp else 'keyword',
                    'source': 'オリジナル', 'src': 'analysis/rengoku_terms.json'}
            if base:
                term['override_from'] = base['en']
            overlay['terms'].append(term)
        old = term.get('en')
        term.update(en=en, status='project_style', note=NOTE)
        # override_from binds the imported baseline, not the previous overlay.
        if old != en:
            changes.append(dict(catalog=path.name, jp=jp, previous=old, text=en))
    save(path, previous, overlay)

    path, config = read('analysis/rengoku_terms.json')
    previous = copy.deepcopy(config)
    config['sources']['user_spelling_20261010'] = 'User screenshot spelling corrections, 2026-10-10'
    for jp, en in NAMES.items():
        term = next((t for t in config['terms'] if t[0] == jp), None)
        old = {'クロウ・ブルースト': 'Crowe Broost', 'ブルースト': 'Broost',
               'エルガン・ローディック': 'Elgan Rhodic', 'ローディック': 'Rhodic'}[jp]
        if term:
            if term[1] != en and term[1] not in term[5]:
                term[5].append(term[1])
            term[1:5] = [en, term[2], 'user_spelling_20261010', 'project_style']
        else:
            config['terms'].append([jp, en, 'pilot' if 'ブルースト' in jp else 'keyword',
                                    'user_spelling_20261010', 'project_style', [old]])
    config['decisions'] = [NOTE if d.startswith('Crowe Broost preserves') else d for d in config['decisions']]
    if NOTE not in config['decisions']:
        config['decisions'].append(NOTE)
    save(path, previous, config)

    path, characters = read('analysis/characters.json')
    previous = copy.deepcopy(characters)
    for row in characters['characters']:
        if row['jp'] in NAMES:
            row['en'] = NAMES[row['jp']]
            if NOTE not in row.get('scope', ''):
                row['scope'] = row.get('scope', '') + ' ' + NOTE
    save(path, previous, characters)

    scanned = 0
    for path in sorted((ROOT / 'localization/locales/en').glob('*.json')):
        if path.name == 'glossary.json':
            continue  # Imported baseline remains intact.
        data = json.loads(path.read_text(encoding='utf8'))
        previous = copy.deepcopy(data)
        for identity, row in data.get('messages', {}).items():
            scanned += 1
            guard = row.get('source', '') + (row.get('text') or '')
            for target in [row] + list(row.get('occurrence_overrides', {}).values()):
                old = target.get('text') or ''
                new = old
                for jp, before, after in [('ブルースト', 'Broost', 'Bluest'),
                                           ('ローディック', 'Rhodic', 'Roddick'),
                                           ('ローディック', 'Laudic', 'Roddick')]:
                    if jp in guard:
                        new = re.sub(r'(?<![A-Za-z])' + before + r'(?![A-Za-z])', after, new)
                if old != new:
                    target['text'] = new
                    changes.append(dict(catalog=path.name, id=identity, previous=old, text=new))
            if path.name.startswith('STG') and 'notes' in row:
                row['notes'] = [NOTE if n.startswith('Two keyword links remain in source order: Elgan, then Reformists. Surname uses Rhodic')
                                else n for n in row.get('notes', [])]
        save(path, previous, data)

    for relative in ('analysis/battle_terminology_applied.json', 'analysis/non_dialogue_terminology_applied.json'):
        path, report = read(relative)
        previous = copy.deepcopy(report)
        protected = report['do_not_touch']
        if isinstance(protected, dict):
            protected.update(NAMES)
        else:
            protected[:] = ['Crowe Bluest' if n == 'Crowe Broost' else n for n in protected]
            for en in NAMES.values():
                if en not in protected:
                    protected.append(en)
        report['name_spelling_20261010'] = NOTE
        save(path, previous, report)

    print(json.dumps(changes, ensure_ascii=False, indent=2))
    print('WRITE' if args.write else 'DRY RUN', len(changes), 'name changes;', scanned, 'locale records scanned;', len(outputs), 'files updated')
    if args.write:
        for path, body in outputs.items():
            path.write_text(body, encoding='utf8')


if __name__ == '__main__':
    main()
