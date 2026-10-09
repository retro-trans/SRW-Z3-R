"""Offline, authenticated extraction of this title's NPDRM program ELF.

Public format/key constants and RAP transform follow RPCS3 Crypto/{unself.cpp,
key_vault.cpp,key_vault.h}. License bytes never enter logs or output manifests.
"""
import argparse
import hashlib
import hmac
import json
from pathlib import Path
import struct
import zlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(__file__).resolve().parents[1]
CONTENT = 'JP0700-NPJB00689_00-SRWZ3RENDLGPKG00'


def aes(raw, key, mode):
    dec = Cipher(algorithms.AES(key), mode).decryptor()
    return dec.update(raw) + dec.finalize()


def license_key(rap):
    if len(rap) != 16:
        raise ValueError('Invalid license size')
    key = bytearray(aes(rap, bytes.fromhex('869f7745c13fd890ccf29188e3cc3edf'), modes.CBC(bytes(16))))
    order = bytes.fromhex('0c030604010b0f08020700050a0e0d09')
    e1 = bytes.fromhex('a93e1fd67c55a329b75fdda62a95c7a5')
    e2 = bytes.fromhex('67d45da3296d006a4e7c537bf5538c74')
    for _ in range(5):
        for p in order:
            key[p] ^= e1[p]
        for i in range(15, 0, -1):
            key[order[i]] ^= key[order[i-1]]
        carry = 0
        for p in order:
            value = (key[p] - carry) & 255
            if carry != 1 or value != 255:
                carry = int(value < e2[p])
            key[p] = (value - e2[p]) & 255
    return aes(bytes(key), bytes.fromhex('f2fbca7a75b04edc1390638ccdfdd1ee'), modes.ECB())


def decrypt(data, rap):
    magic, version, rev, kind, mo, hs, size = struct.unpack_from('>IIHHIQQ', data)
    if (magic, version, rev, kind) != (0x53434500, 2, 0x1c, 1):
        raise ValueError('Unsupported SELF revision')
    ext = struct.unpack_from('>10Q', data, 32)
    if struct.unpack_from('>QIIQQ', data, ext[1])[2] != 8:
        raise ValueError('Expected NPDRM SELF')
    pos, found = ext[7], False
    while pos < ext[7] + ext[8]:
        typ, length, _ = struct.unpack_from('>IIQ', data, pos)
        if length < 16 or pos + length > ext[7] + ext[8]:
            raise ValueError('Invalid control record')
        if typ == 3:
            npd = data[pos+16:pos+length]
            if npd[:4] != b'NPD\0' or struct.unpack_from('>I', npd, 8)[0] != 2 or npd[16:64].rstrip(b'\0').decode('ascii') != CONTENT:
                raise ValueError('Unexpected license identity')
            found = True
        pos += length
    if not found or not mo+96 < hs <= len(data) or size > 64*1024*1024:
        raise ValueError('Invalid SELF metadata bounds')
    wrapped = aes(data[mo+32:mo+96], license_key(rap), modes.CBC(bytes(16)))
    mi = aes(wrapped, bytes.fromhex('8103ea9db790578219c4cedf0592b43064a7d98b601b6c7bc45108c4047aa80f'), modes.CBC(bytes.fromhex('246f4b8328be6a2d394ede20479247c5')))
    if mi[16:32] != bytes(16) or mi[48:64] != bytes(16):
        raise ValueError('License/metadata authentication failed')
    mh = aes(data[mo+96:hs], mi[:16], modes.CTR(mi[32:48]))
    _, _, n, nk, *_ = struct.unpack_from('>Q6I', mh)
    if 32+n*48+nk*16 > len(mh):
        raise ValueError('Metadata key table out of bounds')
    keys = mh[32+n*48:32+n*48+nk*16]
    header = data[ext[2]:ext[2]+64]
    if header[:6] != b'\x7fELF\x02\x02':
        raise ValueError('Expected big-endian ELF64')
    phoff, shoff = struct.unpack_from('>QQ', header, 32)
    phsz, phn, shsz, shn = struct.unpack_from('>4H', header, 54)
    if phsz != 56 or shsz != 64 or phoff+phsz*phn > size or shoff+shsz*shn > size:
        raise ValueError('Invalid ELF tables')
    ph = data[ext[3]:ext[3]+phsz*phn]
    segments = [struct.unpack_from('>IIQQQQQQ', ph, i*phsz) for i in range(phn)]
    out = bytearray(size)
    out[:64], out[phoff:phoff+len(ph)] = header, ph
    verified, omitted = [], []
    for i in range(n):
        off, count, typ, idx, hashed, si, enc, ki, vi, comp = struct.unpack_from('>QQ8I', mh, 32+i*48)
        if off+count > len(data):
            raise ValueError('Payload out of bounds')
        raw = data[off:off+count]
        if enc == 3:
            if max(ki, vi) >= nk:
                raise ValueError('Key index out of bounds')
            raw = aes(raw, keys[ki*16:ki*16+16], modes.CTR(keys[vi*16:vi*16+16]))
        elif enc != 1:
            raise ValueError('Unsupported encryption')
        if typ != 2:
            omitted.append({'type': typ, 'index': idx, 'bytes': count, 'hmac_verified': False})
            continue
        auth = keys[si*16:si*16+96]
        if hashed != 2 or len(auth) != 96 or not hmac.compare_digest(hmac.new(auth[32:], raw, hashlib.sha1).digest(), auth[:20]):
            raise ValueError('Program section HMAC mismatch')
        if comp == 2:
            raw = zlib.decompress(raw)
        elif comp != 1:
            raise ValueError('Unsupported compression')
        s = segments[idx]
        if len(raw) != s[5] or s[2]+len(raw) > size or idx in verified:
            raise ValueError('Program payload extent mismatch')
        out[s[2]:s[2]+len(raw)] = raw
        verified.append(idx)
    if set(verified) != {i for i, s in enumerate(segments) if s[0] == 1}:
        raise ValueError('Not all program loads authenticated')
    out[shoff:shoff+shsz*shn] = data[ext[4]:ext[4]+shsz*shn]
    for i in range(shn):
        _, typ, flags, va, off, count, *_ = struct.unpack_from('>IIQQQQIIQQ', out, shoff+i*shsz)
        if flags & 2 and typ != 8 and count:
            if not any(s[0] == 1 and s[2] <= off and off+count <= s[2]+s[5] and va-off == s[3]-s[2] for s in segments):
                raise ValueError('Unauthenticated allocated section')
    return bytes(out), {'source_sha256': hashlib.sha256(data).hexdigest(), 'elf_sha256': hashlib.sha256(out).hexdigest(), 'program_sections_hmac_verified': verified, 'omitted_metadata': omitted, 'all_allocated_sections_verified': True, 'format': 'Program ELF; original non-program payloads omitted', 'source': 'https://github.com/RPCS3/rpcs3/tree/master/rpcs3/Crypto'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    data = (ROOT / 'work/pkg/USRDIR/EBOOT.BIN').read_bytes()
    elf, report = decrypt(data, (ROOT / (CONTENT + '.rap')).read_bytes())
    print(json.dumps(report, indent=2))
    target = ROOT / 'work/eboot/EBOOT.ELF'
    if target.exists() and target.read_bytes() != elf:
        raise ValueError('Refusing differing ELF')
    print(('WRITE' if args.write else 'DRY RUN') + ': authenticated %d-byte ELF -> %s' % (len(elf), target.relative_to(ROOT)))
    if args.write:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(elf)
        (ROOT / 'analysis/eboot_extraction.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
