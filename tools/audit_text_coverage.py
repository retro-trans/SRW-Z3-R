"""Read-only package text discovery; optional audit artifacts never change sources."""
import argparse
from collections import Counter
import json
import re
import struct
from pathlib import Path
from cpk import CPK
from non_dialogue import ROOT, SOURCE, scan_nul, digest, encoded


def plausible(text):
    # This ranking is deliberately not a coverage proof. Keep candidate counts too.
    return (not re.search(r'[\uff66-\uff9f\ue000-\uf8ff]', text)
            and bool(re.search(r'[\u3041-\u3096\u30a1-\u30fa]{2,}|[\u4e00-\u9fff]{3,}', text)))


def audit():
    source = json.loads(SOURCE.read_text(encoding='utf-8'))
    known_assets = {r['asset'] for r in source['assets']}
    known = {(r['asset'], r['offset']) for r in source['records'] if 'offset' in r}
    assets, candidates, sections = [], [], []
    def scan(key, raw, base=0):
        count = 0
        for off, enc, value in scan_nul(raw):
            count += 1
            if (key, base+off) not in known and plausible(value):
                candidates.append({'asset': key, 'offset': base+off, 'encoding': enc, 'jp': value})
        return count
    for path in sorted((ROOT / 'work/pkg').rglob('*')):
        if not path.is_file():
            continue
        key = path.relative_to(ROOT).as_posix()
        if path.suffix.upper() == '.CPK':
            archive = CPK(str(path))
            family = Counter()
            for entry in archive.files:
                mid = key + ':' + str(entry['id'])
                if '/TALK/' in key or 'TALK' in path.name or '/SOUND/' in key:
                    family['audio_excluded'] += 1
                    continue
                raw = archive.read(entry)
                if mid in known_assets:
                    family['cataloged_asset'] += 1
                elif raw.startswith(b'\x89PNG'):
                    family['png'] += 1
                elif raw[:3] in (b'\x02\x02\x00', b'\x01\x05\x00'):
                    family['gtf_texture'] += 1
                else:
                    family['other_' + raw[:4].hex()] += 1
                    scan(mid, raw)
            assets.append({'asset': key, 'sha256': digest(path.read_bytes()), 'members': len(archive.files), 'types': dict(family)})
            print(path.name, len(archive.files), dict(family), flush=True)
        elif key not in known_assets:
            raw = path.read_bytes()
            kind = 'encrypted' if path.suffix.upper() in ('.SDAT', '.EDAT', '.SELF') or path.name == 'EBOOT.BIN' else 'other'
            if raw.startswith((b'\x89PNG', b'DDS ')):
                kind = 'raster'
            if '/SOUND/' in key:
                kind = 'audio_excluded'
            if kind == 'other':
                count = scan(key, raw)
            else:
                count = None
            assets.append({'asset': key, 'sha256': digest(raw), 'bytes': len(raw), 'type': kind, 'nul_candidates': count})
    path = ROOT / 'work/eboot/EBOOT.ELF'
    raw = path.read_bytes()
    shoff = struct.unpack_from('>Q', raw, 40)[0]
    size, count = struct.unpack_from('>HH', raw, 58)
    for i in range(count):
        _, typ, flags, _, offset, length, _, _, _, _ = struct.unpack_from('>IIQQQQIIQQ', raw, shoff+i*size)
        if typ == 8 or flags & 4:
            continue
        n = scan(path.relative_to(ROOT).as_posix(), raw[offset:offset+length], offset)
        sections.append({'section': i, 'offset': offset, 'bytes': length, 'flags': flags, 'nul_candidates': n})
    return {'source_catalog_sha256': digest(SOURCE.read_bytes()), 'assets': assets, 'elf_sections': sections,
            'unclassified_candidates': candidates,
            'limitations': ['NUL-delimited UTF-8/CP932 discovery is heuristic; short or embedded binary strings can be missed.', 'Raster artwork and font atlases require separate visual inspection.', 'Audio excluded from text translation.']}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    report = audit()
    print('Package assets:', len(report['assets']), '; ELF non-code sections:', len(report['elf_sections']))
    print('Unclassified plausible candidates:', len(report['unclassified_candidates']))
    print(dict(Counter(x['asset'] for x in report['unclassified_candidates'])))
    for row in report['unclassified_candidates'][:30]:
        print(row['asset'], hex(row['offset']), repr(row['jp'][:100]))
    if args.write:
        (ROOT / 'work/text_coverage_candidates.json').write_text(encoded(report), encoding='utf-8')
    else:
        print('DRY RUN; pass --write for audit artifacts.')


if __name__ == '__main__':
    main()
