"""Append newly discovered occurrences without changing existing source bindings."""
import argparse
from collections import Counter, defaultdict
import json
from non_dialogue import ROOT, SOURCE, LOCALE, extract, digest, encoded


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--report-name', default='non_dialogue_spacing_extension.json')
    ap.add_argument('--reason', default='Include ideographic spaces in printable source text; no prior bindings changed.')
    args = ap.parse_args()
    old_bytes = SOURCE.read_bytes()
    old = json.loads(old_bytes)
    fresh = extract()
    a = {r['id']: r for r in old['records']}
    b = {r['id']: r for r in fresh['records']}
    for identity, row in a.items():
        if b.get(identity) != row:
            raise ValueError('Existing source binding changed: ' + identity)
    fresh_assets = {r['asset']: r for r in fresh['assets']}
    if any(fresh_assets.get(r['asset']) != r for r in old['assets']) or any(r not in fresh['exclusions'] for r in old['exclusions']):
        raise ValueError('Existing source assets or exclusions changed')
    additions = [r for r in fresh['records'] if r['id'] not in a]
    locale = json.loads(LOCALE.read_text(encoding='utf-8'))
    if locale['source_catalog_sha256'] != digest(old_bytes):
        raise ValueError('Locale source mismatch')
    output = dict(old)
    output['assets'] = fresh['assets']
    output['records'] = old['records'] + additions
    output['exclusions'] = old['exclusions'] + [r for r in fresh['exclusions'] if r not in old['exclusions']]
    if additions:
        output.setdefault('compatible_catalog_hashes', []).append(digest(old_bytes))
    new_ids = []
    for r in additions:
        identity = r['group'] + ':' + digest(r['jp'].encode())[:16]
        if identity not in locale['messages']:
            locale['messages'][identity] = {'source': r['jp'], 'text': None,
                'status': 'untranslated', 'occurrences': [],
                'source_sha256': r['source_sha256']}
            new_ids.append(identity)
        entry = locale['messages'][identity]
        if entry['source'] != r['jp']:
            raise ValueError('Message identity collision')
        entry['occurrences'].append(r['id'])
    output_bytes = encoded(output).encode('utf-8')
    locale['source_catalog_sha256'] = digest(output_bytes)
    print('New occurrences:', len(additions), dict(Counter(r['group'] for r in additions)))
    print('New message IDs:', len(new_ids))
    for r in additions[:12]:
        print(r['group'], r['locator'], repr(r['jp'][:100]))
    if args.write and additions:
        snapshot = ROOT / 'source/non_dialogue_history' / (digest(old_bytes) + '.json')
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        if snapshot.exists() and snapshot.read_bytes() != old_bytes:
            raise ValueError('History snapshot collision')
        snapshot.write_bytes(old_bytes)
        SOURCE.write_bytes(output_bytes)
        LOCALE.write_text(encoded(locale), encoding='utf-8')
        report = {'previous_catalog_sha256': digest(old_bytes),
            'new_catalog_sha256': digest(output_bytes), 'added_occurrences': additions,
            'added_messages': new_ids, 'reason': args.reason}
        (ROOT / 'analysis' / args.report_name).write_text(encoded(report), encoding='utf-8')
    elif not args.write:
        print('DRY RUN; pass --write after inspection.')


if __name__ == '__main__':
    main()
