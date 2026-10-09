"""Decrypt Rengoku stage archives and extract source records; dry-run by default.

Uses the locally snapshotted Z3 CPK reader and make_npdata, never an emulator.
Outputs must be new: original package contents are never edited.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from cpk import CPK
import luarec

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    archives = sorted((ROOT / 'work/pkg/USRDIR/DATA_REN/STAGE').glob('*.SDAT'))
    if not archives:
        raise SystemExit('No extracted stage archives')
    if (ROOT / 'source/story').exists() or (ROOT / 'work/story').exists():
        raise SystemExit('Story output already exists; refusing overwrite')
    for archive in archives:
        print(f'{archive.relative_to(ROOT)} -> work/story/{archive.stem}.cpk; source/story/{archive.stem}_*.json')
    if not args.write:
        print('DRY RUN; --write decrypts copies and extracts complete, untruncated source records.')
        return
    (ROOT / 'work/story').mkdir(parents=True)
    (ROOT / 'source/story').mkdir(parents=True)
    inventory = []
    for archive in archives:
        dest = ROOT / 'work/story' / (archive.stem + '.cpk')
        result = subprocess.run([str(ROOT / 'work/toolchain/make_npdata.exe'), '-d', str(archive), str(dest), '0'],
                                capture_output=True, timeout=90)
        (dest.with_suffix('.decrypt.log')).write_bytes(result.stdout + result.stderr)
        if result.returncode or not dest.exists() or dest.read_bytes()[:4] != b'CPK ':
            raise SystemExit(f'Decryption failed; see {dest.with_suffix(".decrypt.log")}')
        cpk = CPK(str(dest))
        for entry in cpk.files:
            data = cpk.read(entry)
            member = f'{archive.stem}_{entry["id"]:05d}'
            row = {'archive': archive.name, 'member': entry['id'], 'bytes': len(data),
                   'sha256': hashlib.sha256(data).hexdigest()}
            if b'\0' not in data:
                try:
                    text = data.decode('cp932')
                except UnicodeDecodeError:
                    text = None
                if text is not None and ('--' in text or '=' in text):
                    (ROOT / 'work/story' / (member + '.lua')).write_bytes(data)
                    records = luarec.records(text)
                    for index, record in enumerate(records):
                        record['id'] = f'rengoku:{member}:{index:05d}'
                        record['index'] = index
                        record['source_member_sha256'] = row['sha256']
                    row['records'] = len(records)
                    (ROOT / 'source/story' / (member + '.json')).write_text(
                        json.dumps({'member': member, 'sha256': row['sha256'], 'records': records}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            inventory.append(row)
            print(f'{member}: {len(data):,} bytes, {row.get("records", "binary")} records')
    report = {'members': inventory, 'total_records': sum(x.get('records', 0) for x in inventory),
              'note': 'All parsed long-bracket text; dialogue, narration, banners and any other records are not yet classified.'}
    (ROOT / 'source/story/manifest.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'Total: {report["total_records"]:,} source records')


if __name__ == '__main__':
    main()
