"""Propose exact-source reuse of canonical reference English, with provenance."""
import argparse
from collections import defaultdict, Counter
import json
from pathlib import Path
import unicodedata
import localization
from non_dialogue import ROOT, LOCALE, digest, encoded


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--canonical-names', action='store_true', help='Resolve short-label conflicts using dedicated name catalogs only')
    ap.add_argument('--report-name', help='Separate provenance filename for later extraction batches')
    args = ap.parse_args()
    base = ROOT.parent / 'SRW Z3/localization'
    index = defaultdict(list)
    files = {}
    terms = localization.terms()
    for p in sorted((base / 'messages').glob('*.json')):
        if args.canonical_names and p.stem not in ('glossary', 'parts', 'skills', 'spirits', 'abilities', 'enemy_names', 'map_locations', 'name_pieces'):
            continue
        if p.stem.startswith(('stage', 'STG', 'voice', 'suspend')):
            continue
        q = base / 'locales/en' / p.name
        if not q.exists():
            continue
        definitions = json.loads(p.read_text(encoding='utf-8'))['messages']
        english = json.loads(q.read_text(encoding='utf-8'))['messages']
        for identity, definition in definitions.items():
            jp = definition.get('source')
            target = english.get(identity, {}).get('text')
            if isinstance(jp, str) and target:
                try:
                    expanded = localization.expand(target, terms)
                except ValueError:
                    continue
                index[jp].append({'id': identity, 'text': target, 'expanded': expanded, 'definition': str(p), 'locale': str(q)})
    locale = json.loads(LOCALE.read_text(encoding='utf-8'))
    proposals = []
    for identity, entry in locale['messages'].items():
        if entry['text'] or entry['status'].startswith('excluded'):
            continue
        if args.canonical_names and ('\n' in entry['source'] or len(entry['source']) > 48):
            continue
        matches = index.get(entry['source'], [])
        if len({m['expanded'] for m in matches}) != 1:
            continue
        match = matches[0]
        # Preserve exact-source provenance, never substitute a merely similar line.
        entry.update(text=match['text'], status='reference_draft', reference={'message': match['id'], 'definition': match['definition'], 'locale': match['locale'], 'match': 'exact Japanese source; requires context review'})
        for key in ('definition', 'locale'):
            path = Path(match[key])
            if str(path) not in files:
                files[str(path)] = digest(path.read_bytes())
        proposals.append((identity, entry))
    print('Exact-source draft proposals:', len(proposals), dict(Counter(k.split(':')[0] for k, _ in proposals)))
    for identity, entry in proposals[:18]:
        print(identity, repr(entry['source']), '->', repr(entry['text']))
    if args.write:
        LOCALE.write_text(encoded(locale), encoding='utf-8')
        report = ROOT / 'analysis' / (args.report_name or ('non_dialogue_name_reference_provenance.json' if args.canonical_names else 'non_dialogue_reference_provenance.json'))
        report.write_text(encoded({'files': files, 'entries': [k for k, _ in proposals], 'policy': 'Exact source only. Context/meaning review remains required; no similarity matching.'}), encoding='utf-8')
    else:
        print('DRY RUN; pass --write after inspection.')


if __name__ == '__main__':
    main()
