"""Propose newline-composed labels from exact, unambiguous local translations."""
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
import localization
from non_dialogue import LOCALE, encoded


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('output', type=Path)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    locale = json.loads(LOCALE.read_text(encoding='utf-8'))['messages']
    glossary = localization.terms()
    index = defaultdict(set)
    for entry in locale.values():
        if entry.get('text') and entry['status'] not in ('needs_review', 'preserved_runtime'):
            en = localization.expand(entry['text'], glossary)
            if not any(0xe000 <= ord(c) <= 0xf8ff for c in en):
                index[entry['source']].add(en)
    for term in glossary:
        if term.get('en') and '\n' not in term['jp']:
            index[term['jp']].add(term['en'])
    proposal = {'by_id': {}}
    for identity, entry in locale.items():
        if entry['status'] != 'untranslated' or '\n' not in entry['source']:
            continue
        lines, ok = [], True
        for line in entry['source'].split('\n'):
            if line == '' or re.fullmatch(r'[－―ー—─\-]+', line):
                lines.append(line.replace('ー', '—'))
            elif len(index[line]) == 1:
                lines.append(next(iter(index[line])))
            else:
                ok = False
                break
        if ok:
            text = '\n'.join(lines)
            proposal['by_id'][identity] = {'source': entry['source'], 'text': text,
                'notes': 'Composed from exact local/glossary labels separated by the original newlines. Context and layout require proofreading.'}
            print(identity, repr(entry['source']), '->', repr(text))
            if len(proposal['by_id']) == 80:
                break
    print('Proposals:', len(proposal['by_id']))
    if args.write:
        if args.output.exists():
            raise ValueError('Refusing to overwrite proposal')
        args.output.write_text(encoded(proposal), encoding='utf-8')
    else:
        print('DRY RUN; pass --write after inspection.')


if __name__ == '__main__':
    main()
