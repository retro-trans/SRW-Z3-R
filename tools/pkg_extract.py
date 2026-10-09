"""Inspect/extract a retail PS3 PKG into a NEW directory; dry-run by default.

Format reference: RPCS3 rpcs3/Crypto/unpkg.{h,cpp} and key_vault.h.
Only retail PS3 packages (0x8000, platform 1) are supported. This unwraps
the package container; embedded SDAT/SELF files retain their own encryption.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import struct
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(__file__).resolve().parents[1]
PKG_KEY = bytes.fromhex('2e7b71d7c9c9a14ea3221f188828b8f8')


def safe_relative(name):
    path = PurePosixPath(name)
    if (not name or path.is_absolute() or any(x in ('', '.', '..') for x in name.split('/'))
            or '\\' in name or ':' in name or '\0' in name
            or any(x.endswith((' ', '.')) for x in path.parts)):
        raise ValueError(f'Unsafe package path: {name!r}')
    reserved = {'CON', 'PRN', 'AUX', 'NUL'} | {f'{p}{n}' for p in ('COM', 'LPT') for n in range(1, 10)}
    if any(p.split('.')[0].upper() in reserved for p in path.parts):
        raise ValueError(f'Reserved package path: {name!r}')
    return path


class Package:
    def __init__(self, path):
        self.path = Path(path)
        with self.path.open('rb') as source:
            header = source.read(128)
        if len(header) != 128 or header[:4] != b'\x7fPKG':
            raise ValueError('Not a PKG')
        if struct.unpack_from('>HH', header, 4) != (0x8000, 1):
            raise ValueError('Only retail PS3 packages supported')
        self.count = struct.unpack_from('>I', header, 0x14)[0]
        total, self.offset, self.size = struct.unpack_from('>QQQ', header, 0x18)
        if total != self.path.stat().st_size or self.offset + self.size > total:
            raise ValueError('Package is truncated or size fields disagree')
        if not 0 < self.count <= min(1000000, self.size // 32):
            raise ValueError('Invalid file count')
        self.content_id = header[0x30:0x60].rstrip(b'\0').decode('ascii')
        self.iv = int.from_bytes(header[0x70:0x80], 'big')

    def read(self, offset, size):
        if offset < 0 or size < 0 or offset + size > self.size:
            raise ValueError('Entry exceeds package data range')
        aligned = offset // 16 * 16
        skip = offset - aligned
        counter = (self.iv + aligned // 16).to_bytes(16, 'big')
        cipher = Cipher(algorithms.AES(PKG_KEY), modes.CTR(counter)).decryptor()
        with self.path.open('rb') as source:
            source.seek(self.offset + aligned)
            encrypted = source.read(skip + size)
        if len(encrypted) != skip + size:
            raise ValueError('Short package read')
        return (cipher.update(encrypted) + cipher.finalize())[skip:]

    def entries(self):
        table = self.read(0, self.count * 32)
        entries, names = [], set()
        for idx in range(self.count):
            noff, nsize, off, size, flags, reserved = struct.unpack_from('>IIQQII', table, idx * 32)
            name = self.read(noff, nsize).decode('utf-8').rstrip('\0')
            safe_relative(name)
            if name.casefold() in names:
                raise ValueError(f'Duplicate package path: {name}')
            names.add(name.casefold())
            kind = flags & 0xff
            if kind not in (1, 2, 3, 4, 9):
                raise ValueError(f'Unsupported entry flags {flags:x}: {name}')
            if off + size > self.size:
                raise ValueError(f'Out-of-bounds payload: {name}')
            entries.append({'path': name, 'offset': off, 'size': size, 'flags': flags, 'directory': kind == 4})
        return entries


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('pkg', type=Path)
    ap.add_argument('--out', type=Path, default=ROOT / 'work/pkg')
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    package = Package(args.pkg)
    entries = package.entries()
    root = args.out.resolve()
    root.relative_to(ROOT)
    if root.exists():
        raise SystemExit('Output must be a NEW directory')
    print(f'{package.content_id}: {len(entries)} entries, {sum(e["size"] for e in entries):,} bytes')
    for entry in entries[:20]:
        print(f'  {entry["size"]:>12,}  {entry["path"]}')
    if not args.write:
        print(f'DRY RUN; --write extracts all entries to {root}')
        return
    root.mkdir(parents=True)
    for entry in entries:
        target = root.joinpath(*safe_relative(entry['path']).parts)
        target.resolve().relative_to(root)
        if entry['directory']:
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256()
        with target.open('xb') as output:
            for pos in range(0, entry['size'], 4 * 1024 * 1024):
                data = package.read(entry['offset'] + pos, min(4 * 1024 * 1024, entry['size'] - pos))
                output.write(data)
                digest.update(data)
        entry['sha256'] = digest.hexdigest()
    digest = hashlib.sha256()
    with args.pkg.open('rb') as source:
        for chunk in iter(lambda: source.read(4 * 1024 * 1024), b''):
            digest.update(chunk)
    manifest = {'content_id': package.content_id, 'package_sha256': digest.hexdigest(), 'entries': entries}
    (root / 'extraction_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'Extracted {len(entries)} entries. SHA-256 recorded for package and every file.')


if __name__ == '__main__':
    main()
