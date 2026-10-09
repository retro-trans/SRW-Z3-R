"""Apply source-checked proofreading reports and classify proven binary candidates."""
import argparse
import json
from pathlib import Path
from collections import Counter
from non_dialogue import LOCALE, SOURCE, encoded, digest
import localization


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('reports', nargs='+', type=Path)
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--artwork', action='store_true', help='Review the separate visual-transcription catalog')
    args = ap.parse_args()
    source_path = SOURCE.with_name('artwork.json') if args.artwork else SOURCE
    locale_path = LOCALE.with_name('artwork.json') if args.artwork else LOCALE
    locale = json.loads(locale_path.read_text(encoding='utf-8'))
    count = Counter()
    for path in args.reports:
        report = json.loads(path.read_text(encoding='utf-8'))
        if report.get('source_catalog_sha256') and report['source_catalog_sha256'] != digest(source_path.read_bytes()):
            current_source = json.loads(source_path.read_text(encoding='utf-8'))
            previous = report['source_catalog_sha256']
            history = SOURCE.parent / 'non_dialogue_history' / (previous + '.json')
            if previous not in current_source.get('compatible_catalog_hashes', []) or not history.exists() or digest(history.read_bytes()) != previous:
                raise ValueError('Review source catalog mismatch')
            current_rows = {r['id']: r for r in current_source['records']}
            if any(current_rows.get(r['id']) != r for r in json.loads(history.read_bytes())['records']):
                raise ValueError('Historic review bindings changed')
        for identity, fix in report.get('fixes', {}).items():
            entry = locale['messages'][identity]
            if fix.get('source', entry['source']) != entry['source']:
                raise ValueError('Review source mismatch: ' + identity)
            localization.expand(fix['text'], localization.terms())
            print(identity, repr(entry['text']), '->', repr(fix['text']))
            status = fix.get('status', 'needs_review' if entry['status'] == 'needs_review' else 'reviewed')
            if status not in ('reviewed', 'needs_review'):
                raise ValueError('Unsupported review status')
            entry.update(text=fix['text'], status=status, review=str(path), notes=fix['notes'])
            count['fixes'] += 1
        for identity, decision in report.get('exclusions', {}).items():
            entry = locale['messages'][identity]
            if entry['text']:
                raise ValueError('Cannot exclude a translated entry without explicit review')
            if decision.get('source', entry['source']) != entry['source']:
                raise ValueError('Exclusion source mismatch: ' + identity)
            status = decision.get('status', 'excluded_charset' if entry['status'] == 'excluded_charset' else 'excluded_binary')
            if status not in ('excluded_binary', 'excluded_charset'):
                raise ValueError('Unsupported exclusion status')
            entry.update(status=status, review=str(path), notes=decision.get('reason', decision.get('notes', str(decision))))
            count[status] += 1
        # Classification is separate from English so Japanese input character
        # grids remain intact and do not falsely inflate untranslated prose.
        if path.name == 'interface.json':
            for decision in report['uncertainties']:
                if decision['notes'].startswith('Kana and JIS-ordered kanji rows'):
                    for identity in decision['ids']:
                        entry = locale['messages'][identity]
                        if entry['text']:
                            raise ValueError('Unexpected translated character grid')
                        entry.update(status='excluded_charset', review=str(path), notes=decision['notes'])
                        count['character grid exclusions'] += 1
        for identity in report.get('english_reviewed', report.get('examined', [])):
            entry = locale['messages'][identity]
            if entry['text'] and not identity in report.get('fixes', {}):
                entry.setdefault('reviews', []).append(str(path)) if str(path) not in entry.get('reviews', []) else None
    print(dict(count))
    if args.write:
        locale_path.write_text(encoded(locale), encoding='utf-8')
    else:
        print('DRY RUN; pass --write after inspection.')


if __name__ == '__main__':
    main()
