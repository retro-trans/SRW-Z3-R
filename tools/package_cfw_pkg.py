"""Build a NEW local CFW debug PKG from verified build 018; preview by default.

Debug container/authentication follows PSL1GHT tools/ps3py/pkg.py. SHA-1 stream
decryption is independently documented in RPCS3 Crypto/unpkg.cpp. No SELF
metadata, activation, license, original source or existing output is modified.
The installed plaintext stage is a raw entry, so it is not decrypted twice.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess

from apply_release import identity
from build_game import ROOT, PKG, checked_output, file_inventory
from package_cfw_overlay import CONTENT, STAGE, audit_program, prepare
from pkg_extract import Package, safe_relative
from rengoku_runtime import require

CHUNK = 4 << 20
NATIVE_SOURCE = r'''
#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned char *(*sha1_fn)(const unsigned char *, size_t, unsigned char *);
int main(int argc, char **argv) {
    if(argc != 5 || strlen(argv[2]) != 32) return 2;
    HMODULE lib = LoadLibraryA(argv[1]);
    sha1_fn sha1 = lib ? (sha1_fn)GetProcAddress(lib, "SHA1") : NULL;
    if(!sha1) return 3;
    unsigned char seed[16], context[64] = {0}, hash[20];
    for(int i=0; i<16; i++) { unsigned int v;
        if(sscanf(argv[2]+i*2, "%2x", &v) != 1) return 4;
        seed[i] = (unsigned char)v;
    }
    memcpy(context,seed,8); memcpy(context+8,seed,8);
    memcpy(context+16,seed+8,8); memcpy(context+24,seed+8,8);
    FILE *src = fopen(argv[3], "rb"), *dst = fopen(argv[4], "wb");
    if(!src || !dst) return 5;
    size_t capacity = 4*1024*1024, n;
    unsigned char *buf = malloc(capacity);
    if(!buf) return 6;
    uint64_t block = 0;
    while((n=fread(buf,1,capacity,src)) != 0) {
        for(size_t pos=0; pos<n; pos+=16,block++) {
            for(int i=0; i<8; i++) context[63-i]=(unsigned char)(block>>(i*8));
            if(!sha1(context,64,hash)) return 7;
            size_t count = n-pos < 16 ? n-pos : 16;
            for(size_t i=0; i<count; i++) buf[pos+i] ^= hash[i];
        }
        if(fwrite(buf,1,n,dst) != n) return 8;
    }
    if(ferror(src) || fclose(dst)) return 9;
    fclose(src); free(buf); FreeLibrary(lib); return 0;
}
'''


def align(n):
    return (n + 15) & ~15


def debug_crypt(seed, data, offset=0):
    """Small independent Python reference, also supports unaligned reads."""
    require(len(seed) == 16 and offset >= 0, 'Invalid debug seed/offset')
    prefix = seed[:8] * 2 + seed[8:] * 2 + bytes(24)
    result = bytearray()
    pos = 0
    while pos < len(data):
        block, skip = divmod(offset + pos, 16)
        digest = hashlib.sha1(prefix + struct.pack('>Q', block)).digest()
        count = min(16 - skip, len(data) - pos)
        result.extend(x ^ y for x, y in zip(data[pos:pos + count], digest[skip:]))
        pos += count
    return bytes(result)


def layout(entries, files):
    rows = [dict(e) for e in entries]
    cursor = len(rows) * 32
    for row in rows:
        safe_relative(row['path'])
        row['name_offset'] = cursor
        row['name_bytes'] = len(row['path'].encode('utf8'))
        cursor += align(row['name_bytes'])
    names_end = cursor
    for row in rows:
        row['offset'] = cursor
        row['size'] = 0 if row['directory'] else files[row['path']]['bytes']
        if row['path'] == STAGE:
            row['flags'] = 0x80000003
        cursor += align(row['size'])
    table = bytearray(names_end)
    for i, row in enumerate(rows):
        struct.pack_into('>IIQQII', table, i * 32, row['name_offset'],
                         row['name_bytes'], row['offset'], row['size'], row['flags'], 0)
        name = row['path'].encode('utf8')
        table[row['name_offset']:row['name_offset'] + len(name)] = name
    return rows, bytes(table), cursor


def metadata_from_original(pkg, data_size):
    with pkg.open('rb') as f:
        header = f.read(128)
        start, count, size = struct.unpack_from('>III', header, 8)
        f.seek(start)
        # info_size includes the trailing 64-byte metadata authentication.
        require(size >= 64, 'Metadata region too small')
        meta = bytearray(f.read(size - 64))
    pos = 0
    kinds, packets = [], []
    for _ in range(count):
        kind, length = struct.unpack_from('>II', meta, pos)
        require(pos + 8 + length <= len(meta), 'Metadata extent exceeds header')
        if kind == 4:
            require(length == 8, 'Unexpected data-size metadata')
            struct.pack_into('>Q', meta, pos + 8, data_size)
        # Do not carry the retail package's obsolete QA digest. Debug packages
        # use the freshly computed header QA field (PSL1GHT omits packet 7).
        if kind != 7:
            packets.append(bytes(meta[pos:pos + 8 + length]))
        kinds.append(kind)
        pos += 8 + length
    require(pos == len(meta) and kinds.count(4) == 1, 'Incomplete metadata')
    return b''.join(packets), len(packets)


def make_header(count, data_size, meta_size, meta_count, seed=bytes(16)):
    data_offset = 0xc0 + meta_size + 64
    require(data_offset % 16 == 0, 'Unaligned metadata')
    header = bytearray(128)
    struct.pack_into('>4sHHIIIIQQQ', header, 0, b'\x7fPKG', 0, 1, 0xc0,
                     meta_count, meta_size + 64, count, data_offset + data_size + 96,
                     data_offset, data_size)
    header[0x30:0x60] = CONTENT.encode().ljust(48, b'\0')
    header[0x60:0x70] = seed
    # Debug container license field per PSL1GHT; not a game RAP/RIF/license.
    header[0x70:0x80] = debug_crypt(seed, bytes(16), (2**64 - 1) * 16)
    return bytes(header)


def authenticated_prefix(header, metadata):
    hs = hashlib.sha1(header).digest()[3:19]
    ms = hashlib.sha1(metadata).digest()[3:19]
    pad = debug_crypt(ms, bytes(48))
    return header + hs + debug_crypt(hs, pad) + metadata + ms + pad


def native(tool, crypto, seed, source, dest):
    require(not dest.exists(), 'Native cipher destination exists')
    p = subprocess.run([str(tool), str(crypto), seed.hex(), str(source), str(dest)],
                       capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    require(p.returncode == 0, 'Debug cipher failed with code %s' % p.returncode)


def build(pkg, build_dir, output, compiler, crypto, write=False):
    pkg, build_dir, output, compiler, crypto = [Path(p).resolve()
                                               for p in (pkg, build_dir, output, compiler, crypto)]
    output = checked_output(output)
    require(compiler.is_file() and crypto.is_file(), 'Local compiler/OpenSSL unavailable')
    # Reuse complete source/English/CFW executable audit; no output in preview.
    overlay = prepare(build_dir, output, False)
    report = json.loads((build_dir / 'BUILD_REPORT.json').read_text(encoding='utf8'))
    original_id = identity(pkg)
    require(original_id['sha256'] == report['source_pkg_sha256'], 'Wrong original package')
    original = Package(pkg)
    require(original.content_id == CONTENT, 'Wrong original content identity')
    tree = build_dir / 'RPCS3/NPJB00689'
    files = {p: i for p, i in report['game_files'].items() if p != 'extraction_manifest.json'}
    files.update(overlay['target_files'])
    require(len(files) == 77, 'Expected full 77-file game')
    entries = original.entries()
    require({e['path'] for e in entries if not e['directory']} == set(files), 'Inventory differs')
    rows, table, data_size = layout(entries, files)
    metadata, meta_count = metadata_from_original(pkg, data_size)
    header = make_header(len(rows), data_size, len(metadata), meta_count)
    data_offset = struct.unpack_from('>Q', header, 32)[0]
    version=build_dir.name.rsplit('_',1)[1]
    name = 'SRW-Z3-R-NPJB00689-English-build%s-CFW-test1.pkg'%version
    print(json.dumps(dict(format='PS3 debug PKG for CFW', filename=name, game_files=77,
                          bytes=data_offset + data_size + 96, content_id=CONTENT,
                          stage_entry='raw (3), verified installed plaintext',
                          npdrm_self_unchanged=True, original_license_required=True), indent=2), flush=True)
    if not write:
        print('DRY RUN: new full local PKG, authentication/file readbacks, no install/upload.')
        return
    output.mkdir()
    intermediate = output / 'intermediate'
    intermediate.mkdir()
    cfile, tool = intermediate / 'debug_pkg_crypt.c', intermediate / 'debug_pkg_crypt.exe'
    cfile.write_text(NATIVE_SOURCE, encoding='utf8')
    p = subprocess.run([str(compiler), '-O3', '-std=c99', str(cfile), '-o', str(tool)],
                       capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    require(p.returncode == 0, 'Cipher compilation failed: ' + p.stderr.decode(errors='replace'))
    # Known counter transition / final partial block checked against Python SHA-1.
    sample = bytes(range(256)) * 5 + b'end'
    inp, enc = intermediate / 'cipher_sample', intermediate / 'cipher_sample_enc'
    inp.write_bytes(sample)
    native(tool, crypto, bytes(range(16)), inp, enc)
    require(enc.read_bytes() == debug_crypt(bytes(range(16)), sample), 'Native SHA stream mismatch')
    plain = intermediate / 'payload.plain'
    qa = hashlib.sha1()
    stage = build_dir / 'verification/english_stage/STGZ3REN.SDAT.unedat'
    with plain.open('xb') as stream:
        stream.write(table)
        for row in rows:
            if row['directory']:
                continue
            source = stage if row['path'] == STAGE else tree / row['path']
            require(stream.tell() == row['offset'], 'Payload placement disagrees')
            with source.open('rb') as f:
                for block in iter(lambda: f.read(CHUNK), b''):
                    stream.write(block)
                    qa.update(block)
            stream.write(bytes(align(row['size']) - row['size']))
        require(stream.tell() == data_size, 'Payload size disagrees')
    # Upstream QA input header has content/QA/container-license fields zeroed.
    zero_header = bytearray(header)
    zero_header[0x30:0x80] = bytes(80)
    qa.update(zero_header)
    qa.update(table)
    seed = qa.digest()[:16]
    header = make_header(len(rows), data_size, len(metadata), meta_count, seed)
    encrypted = intermediate / 'payload.encrypted'
    print('Encrypting the complete debug package payload...', flush=True)
    native(tool, crypto, seed, plain, encrypted)
    dest = output / name
    with dest.open('xb') as stream:
        stream.write(authenticated_prefix(header, metadata))
        require(stream.tell() == data_offset, 'Prefix length disagrees')
        with encrypted.open('rb') as f:
            shutil.copyfileobj(f, stream, CHUNK)
        stream.write(bytes(96))
    require(dest.stat().st_size == data_offset + data_size + 96, 'Package size disagrees')
    # Extract packaged ciphertext (not the intermediate) and verify the container.
    cipher_check = intermediate / 'package_ciphertext'
    with dest.open('rb') as f, cipher_check.open('xb') as out:
        prefix = f.read(data_offset)
        require(prefix == authenticated_prefix(header, metadata), 'Authentication prefix mismatch')
        remaining = data_size
        while remaining:
            b = f.read(min(remaining, CHUNK))
            require(b, 'Truncated package')
            out.write(b)
            remaining -= len(b)
        require(f.read() == bytes(96), 'Unexpected package trailer')
    decoded = intermediate / 'package_decoded'
    print('Decrypting and checking all 77 packaged files...', flush=True)
    native(tool, crypto, seed, cipher_check, decoded)
    require(identity(decoded) == identity(plain), 'Complete payload round trip failed')
    with decoded.open('rb') as f:
        require(f.read(len(table)) == table, 'File table/names differ')
        for row in rows:
            if row['directory']:
                continue
            f.seek(row['offset'])
            remaining, h = row['size'], hashlib.sha256()
            while remaining:
                b = f.read(min(remaining, CHUNK))
                require(b, 'Truncated extracted member')
                h.update(b)
                remaining -= len(b)
            require(h.hexdigest() == files[row['path']]['sha256'], 'Member differs: ' + row['path'])
    # Independent Python stream check at both ends and a middle counter value.
    with plain.open('rb') as p, cipher_check.open('rb') as e:
        for pos in (0, len(table) + 3, data_size // 2, data_size - 127):
            p.seek(pos); e.seek(pos)
            require(debug_crypt(seed, e.read(127), pos) == p.read(127), 'Cipher sample differs')
    require(file_inventory(PKG) == report['source_files']
            and file_inventory(tree) == report['game_files'] and identity(pkg) == original_id,
            'Read-only game inputs changed')
    evidence = dict(format='CFW debug PKG (not retail-signed)', title_id='NPJB00689',
                    content_id=CONTENT, original=original_id, package=identity(dest),package_name=name,
                    files=files, entries=rows, all_77_members_verified=True,
                    full_cipher_roundtrip=True, independent_sha1_samples_passed=True,
                    debug_authentication_verified=True, source_files_unchanged=True,
                    executable_audit=overlay['executable_audit'],
                    original_edat_and_npdrm_self_preserved=True, licenses_included=False,
                    cfw_install_tested=False, cfw_boot_tested=False, gameplay_tested=False,
                    compiler=identity(compiler), openssl=identity(crypto), cipher=identity(tool))
    (output / 'PKG-VALIDATION.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf8')
    (output / 'INSTALL.md').write_text((ROOT / 'docs/CFW_PKG_TEST.md').read_text(
        encoding='utf8').replace('018',version),encoding='utf8')
    (output / 'SHA256SUMS.txt').write_text(''.join('%s  %s\n' % (identity(output / n)['sha256'], n)
        for n in (name, 'PKG-VALIDATION.json', 'INSTALL.md')), encoding='utf8')
    print('Prepared CFW test PKG:', identity(dest), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pkg', type=Path, required=True)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--compiler', type=Path, default=Path('C:/mingw64/bin/gcc.exe'))
    parser.add_argument('--crypto', type=Path,
                        default=Path('C:/Program Files/OpenVPN/bin/libcrypto-1_1-x64.dll'))
    parser.add_argument('--write', action='store_true')
    a = parser.parse_args()
    build(a.pkg, a.build, a.out, a.compiler, a.crypto, a.write)
