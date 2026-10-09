"""Assemble an 80-row draft from authored whole strings and exact line labels."""
import argparse
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
import localization
from non_dialogue import LOCALE, encoded


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('authored', type=Path)
    ap.add_argument('output', type=Path)
    ap.add_argument('--group', default='menu_resource')
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    data = json.loads(args.authored.read_text(encoding='utf-8'))
    catalog = json.loads(LOCALE.read_text(encoding='utf-8'))['messages']
    glossary = localization.terms()
    index = defaultdict(set)
    for entry in catalog.values():
        if entry.get('text') and entry['status'] not in ('needs_review', 'preserved_runtime'):
            value = localization.expand(entry['text'], glossary)
            if not any(0xe000 <= ord(c) <= 0xf8ff for c in value):
                index[entry['source']].add(value)
    segments = {}
    for filename in data.get('segment_sources', []):
        segments.update(json.loads((args.authored.parent / filename).read_text(encoding='utf-8')).get('segments', {}))
    segments.update(data.get('segments', {}))
    for jp, en in segments.items():
        index[jp] = {en}
    rows = [(k, v) for k, v in catalog.items() if k.startswith(args.group + ':') and v['status'] == 'untranslated'][:80]
    output, missing = {'by_id': {}}, set()
    for identity, entry in rows:
        value = data.get('by_id', {}).get(identity)
        if value is None:
            lines = entry['source'].split('\n')
            if data.get('preserve_line_indents'):
                lines = [line.lstrip(' \t\u3000') for line in lines]
            if data.get('normalize_latin_lines'):
                for line in lines:
                    if not index[line] and not re.search(r'[\u3040-\u30ff\u3400-\u9fff]', line) and re.search(r'[A-Za-zＡ-Ｚａ-ｚ]', line):
                        index[line] = {unicodedata.normalize('NFKC', line)}
            unknown = [line for line in lines if line and len(index[line]) != 1]
            if unknown:
                missing.update(unknown)
                continue
            value = '\n'.join(next(iter(index[line])) if line else '' for line in lines)
        if isinstance(value, str):
            value = {'text': value}
        value = dict(value, source=entry['source'])
        if data.get('preserve_line_indents') and value['text'] is not None:
            source_lines, target_lines = entry['source'].split('\n'), value['text'].split('\n')
            if len(source_lines) != len(target_lines):
                raise ValueError('Line count mismatch while preserving indentation: ' + identity)
            value['text'] = '\n'.join(re.match(r'[ \t\u3000]*', jp).group() + en.lstrip(' \t\u3000')
                                     for jp, en in zip(source_lines, target_lines))
        output['by_id'][identity] = value
        print(identity, repr(entry['source']), '->', repr(value['text']))
    print('Assembled:', len(output['by_id']), 'of', len(rows))
    if missing:
        print('Unresolved exact lines:')
        for line in sorted(missing):
            print(repr(line))
    if args.write:
        if missing or len(output['by_id']) != len(rows):
            raise ValueError('Draft slice incomplete')
        if args.output.exists():
            raise ValueError('Refusing to overwrite proposal')
        args.output.write_text(encoded(output), encoding='utf-8')
    else:
        print('DRY RUN; pass --write after inspection.')


if __name__ == '__main__':
    main()
