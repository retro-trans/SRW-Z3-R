"""Export reviewed public sources without original script fields. Dry-run by default."""
import argparse
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def snapshot(output, write):
    output = output.resolve()
    if output.exists():
        raise ValueError('Refusing to overwrite public snapshot')
    files = [ROOT / 'README.md', ROOT / '.gitignore', ROOT / '.gitattributes', ROOT / 'requirements.txt',
             ROOT / 'AGENTS.md', ROOT / 'BASE_RULES.md', ROOT / 'CHANGELOG.md']
    files += sorted((ROOT / 'tools').glob('*.py'))
    files += sorted((ROOT / 'tests').glob('*.py'))
    files += [p for p in sorted((ROOT / 'docs').glob('*.md')) if p.name not in ('opening_draft.md',)]
    files += sorted((ROOT / 'docs/releases').glob('*.md'))
    files += sorted((ROOT / '.github').glob('*.md'))
    files += [ROOT / 'localization/glossary_additions.json', ROOT / 'localization/title_screen.json']
    locales = sorted((ROOT / 'localization/locales/en').glob('*.json'))
    cleaned = {}
    removed = 0
    for path in locales:
        data = json.loads(path.read_text(encoding='utf8'))
        for row in data['messages'].values():
            if 'source' in row:
                del row['source']; removed += 1
            for key in ('batch', 'meaning_review'):
                row.pop(key, None)
        cleaned[path.relative_to(ROOT)] = data
    print('Public snapshot:', output)
    print('Tool/document files:', len(files), 'English catalogs:', len(locales), 'original text fields removed:', removed)
    print('Exclude work/, source/, localization/messages/, original-text analysis exports and original script reading copies.')
    if not write:
        print('DRY RUN: original workspace unchanged; no public snapshot written.')
        return
    output.mkdir(parents=True)
    for path in files:
        dest = output / path.relative_to(ROOT); dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
        if path.name == 'artwork_en.md':
            import re
            text = dest.read_text(encoding='utf8')
            text = re.sub(r'(?m)^(### label [0-9]+):.*$', r'\1', text)
            dest.write_text(text, encoding='utf8')
    for relative, data in cleaned.items():
        dest = output / relative; dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    # Glossary short lookup keys and research are necessary for $$ references.
    glossary = json.loads((ROOT / 'analysis/glossary.json').read_text(encoding='utf8'))
    glossary['meta'].pop('base_project', None)
    dest = output / 'analysis/glossary.json'; dest.parent.mkdir()
    dest.write_text(json.dumps(glossary, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    (output / 'HANDOFF.md').write_text(
        '# Public repository handoff\n\n'
        'PS3 Rengoku-hen, NPJB00689. Public 0.1.0 corresponds to verified local build 018.\n'
        'Read BASE_RULES.md, docs/LOCAL_SOURCE_DATA.md and docs/RELEASING.md.\n'
        'English locales are publication exports without original script fields;\n'
        'source-dependent checks/builds require matching private local inputs.\n'
        'Preserve IDs, fingerprints, glossary references and runtime wrappers.\n'
        'See docs/releases/0.1.0.md for coverage and gameplay/hardware limits.\n', encoding='utf8')
    print('Wrote public snapshot; original source catalogs and build inputs remain intact.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    snapshot(args.out, args.write)
