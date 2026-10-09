"""Decrypt a copied EBOOT using an isolated headless RPCS3; never starts a game."""
import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    source = ROOT / 'work/pkg/USRDIR/EBOOT.BIN'
    target = ROOT / 'work/eboot/EBOOT.BIN'
    runtime = ROOT / 'work/offline_rpcs3'
    print(f'Copy {source.relative_to(ROOT)} -> {target.relative_to(ROOT)}')
    print('Run isolated rpcs3.exe --headless --decrypt on the copy, with empty input if a key is requested.')
    if not args.write:
        print('DRY RUN; pass --write to perform offline decryption.')
        return
    if target.exists():
        raise ValueError('Refusing existing EBOOT work copy')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    try:
        result = subprocess.run([str(runtime / 'rpcs3.exe'), '--headless', '--decrypt', str(target)], cwd=runtime,
                                input=b'\n', capture_output=True, timeout=40, creationflags=subprocess.CREATE_NO_WINDOW)
        (target.parent / 'decrypt.log').write_bytes(result.stdout + result.stderr)
        print('Decryptor exit:', result.returncode)
    except subprocess.TimeoutExpired as error:
        (target.parent / 'decrypt.log').write_bytes((error.stdout or b'') + (error.stderr or b''))
        print('Decryptor timeout; its child process was stopped.')
    outputs = [p for p in target.parent.iterdir() if p.is_file() and p.read_bytes()[:4] == b'\x7fELF']
    for path in outputs:
        print('ELF:', path.name, path.stat().st_size, 'SHA256', hashlib.sha256(path.read_bytes()).hexdigest())
    if not outputs:
        raise SystemExit('No ELF produced. See local log; original package remains untouched.')


if __name__ == '__main__':
    main()
