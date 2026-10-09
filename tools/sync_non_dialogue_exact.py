"""Reuse unambiguous exact Japanese matches within the reviewed Rengoku catalog."""
import argparse
from collections import defaultdict, Counter
import json
from non_dialogue import LOCALE, encoded
import localization


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    locale = json.loads(LOCALE.read_text(encoding='utf-8'))
    index = defaultdict(list)
    glossary = localization.terms()
    for identity, entry in locale['messages'].items():
        if entry['text'] and entry['text'].strip() and entry['status'] != 'needs_review':
            index[entry['source']].append((identity, entry, localization.expand(entry['text'], glossary)))
    proposals = []
    for identity, entry in locale['messages'].items():
        if entry['text'] or entry['status'] != 'untranslated':
            continue
        choices = index[entry['source']]
        if len({x[2] for x in choices}) == 1:
            src, donor, english = choices[0]
            if any(0xe000 <= ord(c) <= 0xf8ff for c in english):
                continue
            entry.update(text=donor['text'], status='local_exact_draft', reference={'message': src, 'match': 'exact Japanese in Rengoku catalog; context review required'})
            if 'notes' in donor:
                entry['notes'] = donor['notes']
            proposals.append((identity, entry['source'], english))
    print('Exact local proposals:', len(proposals), dict(Counter(k.split(':')[0] for k, _, _ in proposals)))
    for identity, jp, en in proposals[:20]:
        print(identity, repr(jp[:70]), '->', repr(en[:100]))
    if args.write:
        LOCALE.write_text(encoded(locale), encoding='utf-8')
    else:
        print('DRY RUN; pass --write after inspection.')


if __name__ == '__main__':
    main()
