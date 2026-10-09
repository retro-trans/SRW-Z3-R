"""Rengoku source-bound English catalog and validation. Mutations are dry-run by default."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = re.compile(r'\$\$(.*?)\$\$')
PLACEHOLDER = re.compile(r'\$[A-Za-z]')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def source_rows():
    rows = []
    for path in sorted((ROOT / 'source/story').glob('STG*.json')):
        group = read(path)
        for row in group['records']:
            row = dict(row, member=group['member'])
            rows.append(row)
    if not rows:
        raise ValueError('Extract source first')
    if len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Duplicate source IDs')
    return rows


def terms():
    base = read(ROOT / 'analysis/glossary.json')['terms']
    locale = read(ROOT / 'localization/locales/en/glossary.json')['messages']
    result = {t['id']: dict(t, en=locale[t['id']]['text']) for t in base}
    for term in read(ROOT / 'localization/glossary_additions.json')['terms']:
        old = result.get(term['id'])
        if old and (old['jp'] != term['jp'] or old['en'] != term.get('override_from')):
            raise ValueError(f'Glossary override baseline mismatch: {term["id"]}')
        if not old and 'override_from' in term:
            raise ValueError(f'Missing glossary override target: {term["id"]}')
        result[term['id']] = dict(old or {}, **term)
    return list(result.values())


def expand(text, glossary):
    index = defaultdict(list)
    for term in glossary:
        index[term['jp']].append(term)

    def replace(match):
        key = match.group(1)
        lower = key.endswith('|lc')
        if lower:
            key = key[:-3]
        jp, marker, discriminator = key.partition('#')
        candidates = index.get(jp, [])
        if marker:
            candidates = [t for t in candidates if str(t.get('zukan_id')) == discriminator or t['id'] == discriminator]
        spellings = {t['en'] for t in candidates if t.get('en')}
        if len(spellings) != 1:
            raise ValueError(f'Missing or ambiguous glossary reference: {key}')
        value = next(iter(spellings))
        return value.lower() if lower else value

    result = REFERENCE.sub(replace, text)
    if '$$' in result:
        raise ValueError('Malformed glossary reference')
    return result


def validate(row, entry, glossary):
    errors, warnings = [], []
    if entry.get('source_sha') != row['sha']:
        errors.append('Japanese source fingerprint mismatch')
    if entry.get('source_member_sha256') != row['source_member_sha256']:
        errors.append('Source member fingerprint mismatch')
    text = entry.get('text')
    if text is None:
        if entry.get('status') != 'untranslated':
            errors.append('Missing text must have untranslated status')
        return errors, warnings
    if not isinstance(text, str) or not text.strip():
        return errors + ['Translation must be non-empty text'], warnings
    if entry.get('status') not in ('draft', 'needs_review', 'translated', 'reviewed'):
        errors.append('Invalid translation status')
    try:
        english = expand(text, glossary)
    except ValueError as error:
        return errors + [str(error)], warnings
    jp = row['jp'].replace('\r\n', '\n')
    if Counter(PLACEHOLDER.findall(jp)) != Counter(PLACEHOLDER.findall(english)):
        errors.append('Runtime placeholders changed')
    for opening, closing in [('《', '》'), ('「', '」')]:
        if (jp.count(opening), jp.count(closing)) != (english.count(opening), english.count(closing)):
            errors.append(f'Marker counts changed: {opening}{closing}')
    jp_body = jp.partition('\n')[2]
    en_body = english.partition('\n')[2]
    if jp_body.startswith('（') and not (en_body.startswith('（') and en_body.endswith('）')):
        errors.append('Internal-monologue wrapper changed')
    source_links = re.findall(r'《(.*?)》', jp)
    target_links = re.findall(r'《(.*?)》', english)
    for source_link, target_link in zip(source_links, target_links):
        try:
            expected = expand('$$' + source_link + '$$', glossary)
        except ValueError:
            expected = entry.get('link_labels', {}).get(source_link)
        if expected is None or target_link != expected:
            errors.append(f'Keyword link label/order mismatch: {source_link} -> {target_link}')
    if re.search(r'[\u3040-\u30ff\u3400-\u9fff]', english):
        errors.append('Unresolved Japanese text outside glossary references')
    if '[[' in english or ']]' in english:
        errors.append('Lua long-bracket delimiters in translated text')
    lines = english.splitlines()
    if row['pid']:
        jp_name = jp.split('\n')[0]
        names = {t['en'] for t in glossary if t['jp'] == jp_name}
        if names and lines[0] not in names:
            errors.append('Speaker disagrees with glossary')
        if len(lines) < 2:
            errors.append('Dialogue is missing speaker/body separation')
        if any(not line.startswith('　') or line.startswith('　　') for line in lines[2:]):
            errors.append('Continuation indentation must be one fullwidth space')
    if '\r' in english:
        errors.append('Catalog should use LF line endings')
    if len(lines) > 4:
        warnings.append('More than four record lines; Rengoku layout not measured')
    maximum = max(map(len, lines))
    if maximum > 55:
        warnings.append(f'Longest line {maximum} characters; exceeds provisional Z3 drafting guide, NOT a measured Rengoku limit')
    for ref in REFERENCE.findall(text):
        jp_term = ref.split('|')[0].split('#')[0]
        if any(t['jp'] == jp_term and t['status'] == 'proposed' for t in glossary):
            warnings.append(f'Proposed terminology: {jp_term}')
    # Runtime pixel widths and font coverage remain separate from content validation.
    return errors, warnings


def load_catalog():
    return {r['id']: r for r in source_rows()}, {
        p.stem: read(p) for p in sorted((ROOT / 'localization/locales/en').glob('STG*.json'))}


def seed(write):
    grouped = defaultdict(dict)
    for row in source_rows():
        grouped[row['member']][row['id']] = {'text': None, 'status': 'untranslated', 'source_sha': row['sha'],
                                            'source_member_sha256': row['source_member_sha256']}
    outputs = {}
    for member, messages in grouped.items():
        path = ROOT / 'localization/locales/en' / (member + '.json')
        if path.exists():
            raise ValueError(f'Refusing to overwrite catalog: {path.name}')
        outputs[path] = {'schema': 1, 'language': 'en', 'member': member, 'messages': messages}
    print(f'CREATE {len(outputs)} locale files, {sum(len(v["messages"]) for v in outputs.values())} untranslated entries')
    sample = next(iter(outputs.values()))
    print(encoded({'sample': list(sample['messages'].items())[:2]}))
    if write:
        for path, value in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(encoded(value), encoding='utf-8')
    else:
        print('DRY RUN; pass --write to register the source-bound catalog.')


def apply(path, write):
    rows, catalog = load_catalog()
    batch = read(path)
    glossary = terms()
    modified = set()
    changes = []
    for mid, proposal in batch['messages'].items():
        if mid not in rows:
            raise ValueError(f'Unknown source ID: {mid}')
        row = rows[mid]
        group = catalog[row['member']]
        entry = group['messages'][mid]
        if isinstance(proposal, str):
            if batch.get('source_members', {}).get(row['member']) != row['source_member_sha256']:
                raise ValueError(f'Batch source member hash mismatch: {mid}')
            notes = batch.get('notes', {}).get(mid, [])
            proposal = {'text': proposal, 'status': 'needs_review' if mid in batch.get('needs_review', []) else 'draft',
                        'source_sha': row['sha'], 'source_member_sha256': row['source_member_sha256'],
                        'batch': batch['batch'], 'notes': notes}
            if mid in batch.get('link_labels', {}):
                proposal['link_labels'] = batch['link_labels'][mid]
        if entry['text'] is not None and entry != proposal:
            raise ValueError(f'Existing translation needs manual review: {mid}')
        errors, warnings = validate(row, proposal, glossary)
        if errors:
            raise ValueError(f'{mid}: {errors}')
        if warnings:
            print(f'REVIEW {mid}: {warnings}')
        group['messages'][mid] = proposal
        modified.add(row['member'])
        changes.append((mid, proposal['text']))
    print(f'{len(changes)} entries across {len(modified)} members; sample:')
    for mid, text in changes[:5]:
        print(mid, expand(text, glossary))
    if write:
        for member in sorted(modified):
            (ROOT / 'localization/locales/en' / (member + '.json')).write_text(encoded(catalog[member]), encoding='utf-8')
    else:
        print('DRY RUN; pass --write to apply this exact batch.')


def check():
    rows, catalog = load_catalog()
    glossary = terms()
    counts = Counter()
    errors, warnings = [], []
    seen = set()
    for member, group in catalog.items():
        for mid, entry in group['messages'].items():
            if mid in seen or mid not in rows or rows[mid]['member'] != member:
                errors.append([mid, 'Duplicate/unknown/wrong-member ID'])
                continue
            seen.add(mid)
            bad, notes = validate(rows[mid], entry, glossary)
            errors.extend([mid, x] for x in bad)
            warnings.extend([mid, x] for x in notes)
            counts[entry['status']] += 1
    errors.extend([mid, 'Missing locale entry'] for mid in rows.keys() - seen)
    print(encoded({'source_records': len(rows), 'glossary_terms': len(glossary), 'statuses': dict(counts),
                   'errors': errors, 'review_notes': warnings, 'runtime_layout': 'NOT VERIFIED'}))
    return not errors


def preview(out, write):
    rows, catalog = load_catalog()
    glossary = terms()
    lines = ['# Rengoku opening English draft', '',
             'Draft text only. Font support, wrapping, reinsertion and runtime appearance are not verified.', '']
    for mid, row in rows.items():
        entry = catalog[row['member']]['messages'][mid]
        if entry['text'] is None:
            continue
        english = expand(entry['text'], glossary)
        lines.extend([f'## {mid}', '', f"Status: {entry['status']}", '', english.replace('\n', '  \n'), ''])
        if entry.get('notes'):
            lines.extend(['Review: ' + ' '.join(entry['notes']), ''])
    output = out.resolve()
    output.relative_to(ROOT)
    content = '\n'.join(lines)
    print(f'{"WRITE" if write else "DRY RUN"} {output} ({len(content)} characters)')
    print(content[:1000])
    if write:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='command', required=True)
    sub.add_parser('seed').add_argument('--write', action='store_true')
    update = sub.add_parser('apply')
    update.add_argument('batch', type=Path)
    update.add_argument('--write', action='store_true')
    sub.add_parser('check')
    export = sub.add_parser('preview')
    export.add_argument('--out', type=Path, default=ROOT / 'docs/opening_draft.md')
    export.add_argument('--write', action='store_true')
    args = ap.parse_args()
    if args.command == 'seed':
        seed(args.write)
    elif args.command == 'apply':
        apply(args.batch, args.write)
    elif args.command == 'check':
        raise SystemExit(0 if check() else 1)
    else:
        preview(args.out, args.write)


if __name__ == '__main__':
    main()
