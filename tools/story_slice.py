"""Prepare read-only 80-record story translation packets. Dry-run by default; --write writes under work/story_batches."""
import argparse
import json
from pathlib import Path

import localization as L

ROOT = L.ROOT
OUT = ROOT / 'work/story_batches'
SIZE = 80
CONTEXT = 20


def packet(number):
    rows, catalog = L.load_catalog()
    ordered = list(rows.values())
    start, end = SIZE * (number - 1), min(SIZE * number, len(ordered))
    if start >= len(ordered):
        raise ValueError(f'Slice {number} is beyond {len(ordered)} records')
    glossary = L.terms()

    def view(row):
        entry = catalog[row['member']]['messages'][row['id']]
        item = {'id': row['id'], 'event': row['event'], 'pid': row['pid'], 'jp': row['jp'].replace('\r\n', '\n')}
        if entry['text'] is not None:
            item['existing_en'] = L.expand(entry['text'], glossary)
            item['existing_status'] = entry['status']
        return item

    slice_rows = ordered[start:end]
    before = ordered[max(0, start - CONTEXT):start]
    after = ordered[end:end + CONTEXT]
    corpus = '\n'.join(r['jp'] for r in before + slice_rows + after)
    by_jp = {}
    for term in glossary:
        if len(term['jp']) >= 2 and term['jp'] in corpus:
            by_jp.setdefault(term['jp'], []).append(term)
    matched = []
    for jp, found in sorted(by_jp.items(), key=lambda kv: -len(kv[0])):
        spellings = {t['en'] for t in found}
        for t in found:
            item = {'jp': jp, 'en': t['en'], 'kind': t.get('kind'), 'status': t.get('status')}
            if len(spellings) > 1:
                item['reference'] = f"$${jp}#{t.get('zukan_id') or t['id']}$$"
            else:
                item['reference'] = f'$${jp}$$'
            if t.get('note'):
                item['note'] = t['note']
            matched.append(item)
            if len(spellings) == 1:
                break
    characters = [c for c in L.read(ROOT / 'analysis/characters.json')['characters']
                  if c['jp'] in corpus or c['jp'].split('・')[0] in corpus]
    return {
        'slice': number, 'batch': f'story_{number:04d}',
        'source_range': f'Flattened source order {start}..{end - 1} inclusive',
        'source_members': {r['member']: r['source_member_sha256'] for r in slice_rows},
        'context_before': [view(r) for r in before], 'rows': [view(r) for r in slice_rows],
        'context_after': [view(r) for r in after], 'glossary_matches': matched, 'characters': characters,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('slices', type=int, nargs='+')
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    for number in args.slices:
        value = packet(number)
        path = OUT / f'slice_{number:04d}_packet.json'
        print(f"{'WRITE' if args.write else 'DRY RUN'} {path.relative_to(ROOT)}: {value['source_range']}, "
              f"{len(value['rows'])} rows, {len(value['glossary_matches'])} glossary matches, "
              f"{len(value['characters'])} character profiles")
        if args.write:
            OUT.mkdir(parents=True, exist_ok=True)
            path.write_text(L.encoded(value), encoding='utf-8')


if __name__ == '__main__':
    main()
