"""Read-only integrity audit of extracted package, CPK and source records.

An independent Lua lexical walk checks the inherited regex extractor against
comments and quoted strings. Does not claim complete coverage of UI/short strings.
"""
import hashlib
import json
from pathlib import Path
import re
from cpk import CPK
import luarec

ROOT = Path(__file__).resolve().parents[1]
LONG = re.compile(r'\[(=*)\[')


def long_strings(text):
    result = []
    index = 0
    while index < len(text):
        comment = text.startswith('--', index)
        start = index + 2 if comment else index
        match = LONG.match(text, start)
        if match:
            closing = ']' + match.group(1) + ']'
            end = text.find(closing, match.end())
            if end < 0:
                raise ValueError('Unclosed Lua long string/comment')
            if not comment:
                result.append(text[match.end():end])
            index = end + len(closing)
        elif comment:
            end = text.find('\n', index)
            index = len(text) if end < 0 else end + 1
        elif text[index] in ('"', "'"):
            quote = text[index]
            index += 1
            while index < len(text):
                if text[index] == '\\':
                    index += 2
                elif text[index] == quote:
                    index += 1
                    break
                else:
                    index += 1
        else:
            index += 1
    return result


def sha_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(4 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def audit():
    manifest = json.loads((ROOT / 'work/pkg/extraction_manifest.json').read_text(encoding='utf-8'))
    pkgs = list(ROOT.glob('*.pkg'))
    if len(pkgs) != 1 or sha_file(pkgs[0]) != manifest['package_sha256']:
        raise ValueError('Original package hash mismatch or ambiguous package')
    checked_files = 0
    for entry in manifest['entries']:
        if not entry['directory']:
            path = ROOT / 'work/pkg' / entry['path']
            if path.stat().st_size != entry['size'] or sha_file(path) != entry['sha256']:
                raise ValueError(f'Package extraction changed: {entry["path"]}')
            checked_files += 1
    inventory = json.loads((ROOT / 'source/story/manifest.json').read_text(encoding='utf-8'))
    cpk = CPK(str(ROOT / 'work/story/STGZ3REN.cpk'))
    by_id = {r['member']: r for r in inventory['members']}
    record_count = lua_count = 0
    for entry in cpk.files:
        data = cpk.read(entry)
        expected = by_id[entry['id']]
        if len(data) != entry['extract'] or hashlib.sha256(data).hexdigest() != expected['sha256']:
            raise ValueError(f'CPK size/hash mismatch: member {entry["id"]}')
        if 'records' not in expected:
            continue
        name = f'STGZ3REN_{entry["id"]:05d}'
        if (ROOT / 'work/story' / (name + '.lua')).read_bytes() != data:
            raise ValueError(f'Lua file changed: {name}')
        group = json.loads((ROOT / 'source/story' / (name + '.json')).read_text(encoding='utf-8'))
        literal_texts = long_strings(data.decode('cp932'))
        if literal_texts != [r['jp'] for r in group['records']]:
            raise ValueError(f'Independent Lua lexer disagrees: {name}')
        for index, row in enumerate(group['records']):
            if (row['sha'] != luarec.digest(row['jp']) or row['index'] != index
                    or row['source_member_sha256'] != expected['sha256']
                    or row['id'] != f'rengoku:{name}:{index:05d}'):
                raise ValueError(f'Source identity mismatch: {name}:{index}')
        lua_count += 1
        record_count += len(literal_texts)
    if record_count != inventory['total_records']:
        raise ValueError('Source manifest count mismatch')
    return {'original_package_sha256': manifest['package_sha256'], 'extracted_files_verified': checked_files,
            'cpk_members_verified': len(cpk.files), 'lua_members_lexed': lua_count,
            'long_string_records_verified': record_count, 'errors': []}


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
