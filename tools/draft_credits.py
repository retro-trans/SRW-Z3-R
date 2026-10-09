"""Assemble source-guarded credit slices using reviewed whole column labels."""
import argparse
import json
import re
from pathlib import Path
from non_dialogue import ROOT, LOCALE, encoded


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('output', type=Path)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    terms = json.loads((ROOT / 'analysis/credits_terms.json').read_text(encoding='utf-8'))
    catalog = json.loads(LOCALE.read_text(encoding='utf-8'))['messages']
    rows = [(k, v) for k, v in catalog.items() if k.startswith('credits:') and v['status'] == 'untranslated'][:80]
    proposal, missing = {'by_id': {}}, set()
    for key, row in rows:
        if key == 'credits:c5e1a745fecaf60e':
            value = {'text': None, 'status': 'excluded_binary', 'notes': 'False candidate starts at byte 16 inside the binary header. Correct title is separately cataloged at byte 20.'}
        else:
            parts = re.split('(\u3000+)', row['source'])
            unknown = [p for p in parts if p and not p.isspace() and p not in terms['terms']]
            if unknown:
                missing.update(unknown)
                continue
            value = {'text': ''.join(p if not p or p.isspace() else terms['terms'][p] for p in parts)}
            provisional = [p for p in parts if p in terms['provisional']]
            if provisional:
                value.update(status='needs_review', notes='Provisional name reading; verify before publication: ' + ', '.join(provisional))
        value['source'] = row['source']
        proposal['by_id'][key] = value
        print(key, repr(row['source']), '->', repr(value['text']))
    print('Prepared', len(proposal['by_id']), 'of', len(rows), '; missing:', sorted(missing))
    if args.write:
        if missing or args.output.exists():
            raise ValueError('Incomplete proposal or output already exists')
        args.output.write_text(encoded(proposal), encoding='utf-8')
    else:
        print('DRY RUN; pass --write after inspection.')


if __name__ == '__main__':
    main()
