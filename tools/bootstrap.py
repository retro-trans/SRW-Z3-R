"""Seed the English glossary from Z3's canonical catalog. Dry-run by default."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base', type=Path, default=ROOT.parent / 'SRW Z3')
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    base = args.base.resolve()
    inputs = {}

    def read(rel):
        data = (base / rel).read_bytes()
        inputs[rel] = digest(data)
        return data

    messages = json.loads(read('localization/messages/glossary.json'))
    locale = json.loads(read('localization/locales/en/glossary.json'))
    legacy = json.loads(read('platforms/ps3/localization/legacy.json'))
    template = legacy['documents']['analysis/glossary.json']['template']

    def resolve(value):
        if isinstance(value, dict):
            if set(value) == {'$message'}:
                return locale['messages'][value['$message']]['text']
            return {k: resolve(v) for k, v in value.items()}
        if isinstance(value, list):
            return [resolve(v) for v in value]
        return value

    glossary = resolve(template)
    # Store stable source IDs alongside all inherited research and disambiguators.
    for term, original in zip(glossary['terms'], template['terms']):
        term['id'] = original['en']['$message']
    glossary['meta']['base_project'] = str(base)
    glossary['meta']['base_catalog_sha256'] = inputs['localization/locales/en/glossary.json']
    glossary['meta']['note'] = 'Rengoku base, resolved from Z3 canonical English; inherited research is not newly verified.'
    outputs = {
        'localization/messages/glossary.json': messages,
        'localization/locales/en/glossary.json': locale,
        'analysis/glossary.json': glossary,
    }
    copies = {}
    for rel in ('tools/cpk.py', 'tools/luarec.py'):
        copies[rel] = read(rel)
    copies['work/toolchain/make_npdata.exe'] = read('work/make_npdata.exe')
    outputs['analysis/base_provenance.json'] = {
        'base': str(base), 'files': inputs,
        'glossary_entries': len(messages['messages']),
        'note': 'Snapshot only. No source project files modified. Do not copy Z3 executable offsets or width claims to Rengoku.',
    }
    for rel, value in outputs.items():
        copies[rel] = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    for rel, data in copies.items():
        target = ROOT / rel
        if target.exists() and target.read_bytes() != data:
            raise SystemExit(f'Refusing to overwrite different file: {rel}')
        print(f'{"UNCHANGED" if target.exists() else "CREATE"} {rel} ({len(data):,} bytes)')
    print(f"Glossary: {len(glossary['terms'])} terms; sample:")
    for term in glossary['terms'][:5]:
        print(f"  {term['jp']} -> {term['en']}")
    if args.write:
        for rel, data in copies.items():
            target = ROOT / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_bytes(data)
    else:
        print('DRY RUN; pass --write to create these files.')


if __name__ == '__main__':
    main()
