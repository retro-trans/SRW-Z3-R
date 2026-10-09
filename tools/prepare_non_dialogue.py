"""Snapshot read-only helpers and an isolated offline decryptor; preview first."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    base = ROOT.parent / 'SRW Z3'
    pairs = [(base / 'tools' / name, ROOT / 'tools' / name) for name in ('zukan.py', 'rpw.py')]
    pairs.append((ROOT.parent / 'SRW Z3 2/tools/source_text.py', ROOT / 'tools/source_text.py'))
    runtime = Path('E:/RPCS3')
    destination = ROOT / 'work/offline_rpcs3'
    pairs.extend((p, destination / p.name) for p in runtime.iterdir() if p.is_file() and p.suffix.lower() in ('.dll', '.exe') and p.name != 'updater.exe')
    pairs.extend((p, destination / p.relative_to(runtime)) for p in (runtime / 'qt6').rglob('*') if p.is_file())
    provenance = []
    for src, dst in pairs:
        digest = hashlib.sha256(src.read_bytes()).hexdigest()
        if dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest() != digest:
            raise ValueError(f'Different existing tool: {dst}')
        provenance.append({'source': str(src), 'destination': str(dst.relative_to(ROOT)), 'sha256': digest})
    print(f'{len(pairs)} helper/runtime files; {sum(p.stat().st_size for p, _ in pairs):,} bytes')
    for src, dst in pairs[:8]:
        print(f'{src} -> {dst.relative_to(ROOT)}')
    print('No emulator configuration, saves, accounts, firmware or installed games will be copied.')
    if args.write:
        for src, dst in pairs:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists():
                shutil.copyfile(src, dst)
        (ROOT / 'analysis/non_dialogue_tool_provenance.json').write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
    else:
        print('DRY RUN; pass --write to copy tools only.')


if __name__ == '__main__':
    main()
