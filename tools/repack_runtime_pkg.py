"""Build a NEW RPCS3-only PKG from an exact original and verified local build.

Dry-run by default. Retain unchanged encrypted payload at its original offsets;
replace changed files in place when they fit and append larger files. This
preserves binary similarity for xdelta. Original Sony authentication is not
valid after editing: authentication blocks are cleared, and the result is
explicitly for RPCS3, not a signed retail/CFW/HEN installer.

Format reference: RPCS3 rpcs3/Crypto/unpkg.{cpp,h}.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from apply_release import identity
from pkg_extract import Package, PKG_KEY

ROOT = Path(__file__).resolve().parents[1]
CHUNK = 4 * 1024 * 1024


def align(value):
    return (value + 15) // 16 * 16


def placement(entries, changed, sizes, original_size):
    cursor = align(original_size)
    plan = []
    for index, entry in enumerate(entries):
        if entry['path'] not in changed:
            continue
        if entry['directory']:
            raise ValueError('Cannot replace a directory')
        size = sizes[entry['path']]
        offset = entry['offset']
        if offset % 16:
            raise ValueError('Changed payload is not AES-block aligned')
        appended = size > entry['size']
        if appended:
            offset = cursor
            cursor = align(cursor + size)
        plan.append(dict(index=index, path=entry['path'], offset=offset,
                         size=size, appended=appended))
    if {r['path'] for r in plan} != set(changed):
        raise ValueError('Changed file missing from original package')
    return plan, cursor


def cipher(iv, offset):
    if offset % 16:
        raise ValueError('AES payload offset must be block aligned')
    return Cipher(algorithms.AES(PKG_KEY),
                  modes.CTR((iv + offset // 16).to_bytes(16, 'big'))).encryptor()


def digest_member(package, entry):
    digest = hashlib.sha256()
    for pos in range(0, entry['size'], CHUNK):
        digest.update(package.read(entry['offset'] + pos,
                                   min(CHUNK, entry['size'] - pos)))
    return dict(bytes=entry['size'], sha256=digest.hexdigest())


def build(pkg, build_dir, output, write=False):
    pkg, build_dir, output = (Path(p).resolve() for p in (pkg, build_dir, output))
    output.relative_to((ROOT / 'work').resolve())
    if output.exists() or output == pkg or output in pkg.parents:
        raise ValueError('Output must be a NEW directory under work')
    report = json.loads((build_dir / 'BUILD_REPORT.json').read_text(encoding='utf8'))
    validation = json.loads((build_dir / 'verification/RESULT.json').read_text(encoding='utf8'))
    if report['title_id'] != 'NPJB00689' or not validation['all_passed']:
        raise ValueError('Wrong title or failed build validation')
    if identity(pkg)['sha256'] != report['source_pkg_sha256']:
        raise ValueError('Original PKG identity mismatch')
    package = Package(pkg)
    if package.content_id != 'JP0700-NPJB00689_00-SRWZ3RENDLGPKG00':
        raise ValueError('Wrong package content ID')
    entries = package.entries()
    files = {e['path']: e for e in entries if not e['directory']}
    expected = {p: v for p, v in report['game_files'].items()
                if p != 'extraction_manifest.json'}
    if set(files) != set(expected):
        raise ValueError('Package/build file membership differs')
    target = build_dir / 'RPCS3/NPJB00689'
    for name, entry in files.items():
        if digest_member(package, entry) != report['source_files'][name]:
            raise ValueError('Original PKG member mismatch: ' + name)
        if identity(target / name) != expected[name]:
            raise ValueError('Build member changed: ' + name)
    plan, data_size = placement(entries, report['changed_files'],
                                {n: v['bytes'] for n, v in expected.items()}, package.size)
    print('Original PKG:', identity(pkg), flush=True)
    print('New data size:', data_size, 'RPCS3 only; no retail signing', flush=True)
    for row in plan:
        print(row, flush=True)
    if not write:
        print('DRY RUN: new PKG, verify all 77 members; original and build remain unchanged.')
        return
    output.mkdir(parents=True)
    dest = output / 'SRW-Z3-R-NPJB00689-English-build018-RPCS3.pkg'
    shutil.copyfile(pkg, dest)
    with pkg.open('rb') as source:
        header = bytearray(source.read(package.offset))
    # Header sizes and metadata size must describe the modified payload.
    struct.pack_into('>Q', header, 0x18, package.offset + data_size + 96)
    struct.pack_into('>Q', header, 0x28, data_size)
    meta_pos, meta_count, meta_size = struct.unpack_from('>III', header, 8)
    meta_end = meta_pos + meta_size
    for _ in range(meta_count):
        kind, size = struct.unpack_from('>II', header, meta_pos)
        if meta_pos + 8 + size > meta_end:
            raise ValueError('Metadata packet exceeds its declared bounds')
        if kind == 4:
            if size != 8:
                raise ValueError('Unexpected package-size metadata')
            struct.pack_into('>Q', header, meta_pos + 8, data_size)
        meta_pos += 8 + size
    # Do not retain authentication bytes that could be mistaken for valid signing.
    header[0x80:0xc0] = bytes(64)
    table = bytearray(package.read(0, package.count * 32))
    with dest.open('r+b') as stream:
        stream.truncate(package.offset + data_size + 96)
        stream.seek(0)
        stream.write(header)
        for row in plan:
            struct.pack_into('>QQ', table, row['index'] * 32 + 8,
                             row['offset'], row['size'])
            crypt = cipher(package.iv, row['offset'])
            stream.seek(package.offset + row['offset'])
            with (target / row['path']).open('rb') as member:
                for block in iter(lambda: member.read(CHUNK), b''):
                    stream.write(crypt.update(block))
            stream.write(crypt.finalize())
        stream.seek(package.offset)
        crypt = cipher(package.iv, 0)
        stream.write(crypt.update(bytes(table)) + crypt.finalize())
        stream.seek(package.offset + data_size)
        stream.write(bytes(96))
    rebuilt = Package(dest)
    actual = {e['path']: digest_member(rebuilt, e)
              for e in rebuilt.entries() if not e['directory']}
    if actual != expected:
        raise ValueError('Repacked package members differ from complete build')
    evidence = dict(title_id='NPJB00689', content_id=package.content_id,
                    original=identity(pkg), target=identity(dest),
                    build_report_sha256=identity(build_dir / 'BUILD_REPORT.json')['sha256'],
                    files=actual, all_77_members_verified=True,
                    changed_files=plan, signed_retail_package=False,
                    gameplay_tested=False, ps3_hardware_tested=False)
    (output / 'PKG-VALIDATION.json').write_text(
        json.dumps(evidence, indent=2) + '\n', encoding='utf8')
    if identity(pkg)['sha256'] != report['source_pkg_sha256']:
        raise ValueError('Original changed during repacking')
    print('Verified all', len(actual), 'members:', identity(dest), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pkg', type=Path, required=True)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    build(args.pkg, args.build, args.out, args.write)
