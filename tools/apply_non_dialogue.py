"""Apply reviewed exact-source draft maps, previewing every update by default."""
import argparse
import json
from collections import Counter
from pathlib import Path
import localization
from non_dialogue import LOCALE, encoded, digest


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('proposal', type=Path)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    proposal = json.loads(args.proposal.read_text(encoding='utf-8'))
    locale = json.loads(LOCALE.read_text(encoding='utf-8'))
    glossary = localization.terms()
    done, used = [], set()
    for identity, entry in locale['messages'].items():
        if proposal.get('groups') and identity.split(':')[0] not in proposal['groups']:
            continue
        value = proposal.get('by_id', {}).get(identity)
        by_id = value is not None
        if value is None:
            value = proposal.get('by_source', {}).get(entry['source'])
        if value is None:
            continue
        used.add(identity if by_id else entry['source'])
        if isinstance(value, str):
            value = {'text': value}
        if 'source' in value and value['source'] != entry['source']:
            raise ValueError('Proposal source mismatch: ' + identity)
        if entry['text'] and not proposal.get('revise_existing'):
            continue
        text = value['text']
        if text is None:
            if value.get('status') not in ('excluded_charset', 'excluded_dialogue', 'excluded_binary') or not value.get('notes') or value.get('source') != entry['source']:
                raise ValueError('Missing text requires a source-guarded documented exclusion')
        else:
            localization.expand(text, glossary)
        entry.update(text=text, status=value.get('status', 'draft'), batch=args.proposal.name)
        if value.get('notes'):
            entry['notes'] = value['notes']
        done.append((identity, entry['source'], text))
    missing = (set(proposal.get('by_source', {})) | set(proposal.get('by_id', {}))) - used
    if missing:
        raise ValueError('Unknown proposal sources/IDs: ' + repr(sorted(missing)))
    print('Updates:', len(done), dict(Counter(k.split(':')[0] for k, _, _ in done)))
    for key, jp, en in done[:16]:
        print(key, repr(jp[:90]), '->', repr(en[:120] if en is not None else None))
    if args.write:
        LOCALE.write_text(encoded(locale), encoding='utf-8')
    else:
        print('DRY RUN; pass --write after inspection.')


if __name__ == '__main__':
    main()
