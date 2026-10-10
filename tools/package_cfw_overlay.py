"""Prepare a local NPJB00689 CFW hardware-test overlay; dry-run by default.

Only a NEW child of work/builds/ can be written. Builds and original inputs
are read-only. The stage archive uses its verified post-install plaintext,
since copying files does not execute a PKG installer's SDAT decryption.
No full game, licenses, console installation or hardware pass is produced.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
import shutil
import struct
import zipfile

from build_game import ROOT, PKG, checked_output, controls, file_inventory
from rengoku_runtime import CODE, WIDTHS, TEXT, ELF_SHA, require, sha

STAGE = 'USRDIR/DATA_REN/STAGE/STGZ3REN.SDAT'
CONTENT = 'JP0700-NPJB00689_00-SRWZ3RENDLGPKG00'


def identity(path):
    data = Path(path).read_bytes()
    return {'bytes': len(data), 'sha256': sha(data)}


def loads(elf):
    require(elf[:6] == b'\x7fELF\x02\x02', 'Expected big-endian ELF64')
    offset = struct.unpack_from('>Q', elf, 32)[0]
    size, count = struct.unpack_from('>HH', elf, 54)
    require(size == 56 and count == 8, 'Unexpected Rengoku program table')
    return [struct.unpack_from('>IIQQQQQQ', elf, offset + i * size)
            for i in range(count)]


def audit_program(original, elf, wrapped, original_self, runtime):
    require(sha(original) == ELF_SHA == runtime['source_sha256'], 'Wrong original ELF')
    before, after = loads(original), loads(elf)
    active = [r for r in after if r[0] == 1 and r[6]]
    require(len(active) == 2, 'Exactly two active native LOADs required')
    require(before[5:] == after[5:], 'TLS/process metadata changed')
    require(original[24:32] == elf[24:32], 'Entry descriptor changed')
    for old, new in zip(before[:2], after[:2]):
        require(old[:5] == new[:5] and old[7] == new[7], 'Native LOAD mapping changed')
        require(new[5] == new[6] and new[2] + new[5] <= len(elf), 'Incomplete LOAD')
        require(new[2] % new[7] == new[3] % new[7], 'Invalid LOAD alignment')
        require(new[1] & 3 != 3, 'Writable executable segment')
    require(active[0][3] + active[0][6] <= active[1][3], 'LOAD memory overlap')
    require(active[0][1] & 7 == 5 and active[1][1] & 7 == 6, 'Expected RX and RW')
    require(active[1][3] <= TEXT < active[1][3] + active[1][6], 'Text table outside RW')
    tail = before[1][2] + before[1][5]
    require(not any(elf[tail:TEXT - 0x10000]), 'Original BSS/scratch not zero-filled')
    # Restore only recorded edits, then compare all original program bytes.
    restored = bytearray(elf[:tail])
    restored[40:48] = original[40:48]
    restored[64:64 + 8 * 56] = original[64:64 + 8 * 56]
    for row in runtime['edits']:
        lo, count = row['offset'], row['bytes']
        require(lo >= 0 and count > 0 and lo + count <= len(elf), 'Invalid edit extent')
        if lo < tail:
            restored[lo:min(tail, lo + count)] = original[lo:min(tail, lo + count)]
    require(restored == original[:tail], 'Unrecorded original program edit')
    rx = active[0]
    def executable(address):
        return address % 4 == 0 and rx[3] <= address < rx[3] + rx[5]
    require(all(CODE <= address < WIDTHS and executable(address)
                for address in runtime['stubs'].values()), 'Hook outside executable LOAD')
    direct = 0
    for address in range(CODE, WIDTHS, 4):
        word = struct.unpack_from('>I', elf, address - 0x10000)[0]
        opcode = word >> 26
        if opcode not in (16, 18):
            continue
        bits = 16 if opcode == 16 else 26
        displacement = word & ((1 << bits) - 4)
        if displacement & (1 << (bits - 1)):
            displacement -= 1 << bits
        target = displacement if word & 2 else address + displacement
        require(executable(target), 'Injected direct branch outside executable LOAD')
        direct += 1
    require(wrapped[:4] == b'SCE\0' and struct.unpack_from('>IHH', wrapped, 4)
            == (2, 0x8000, 1), 'Expected CFW fake SELF')
    payload, count = struct.unpack_from('>QQ', wrapped, 16)
    require(count == len(elf) and wrapped[payload:] == elf, 'SELF payload differs')
    old_app = struct.unpack_from('>Q', original_self, 0x28)[0]
    new_app = struct.unpack_from('>Q', wrapped, 0x28)[0]
    require(original_self[old_app:old_app + 32] == wrapped[new_app:new_app + 32],
            'NPDRM application identity changed')
    old_control, new_control = controls(original_self), controls(wrapped)
    for kind in (1, 3):
        old, length = old_control[kind]
        new, new_length = new_control[kind]
        require(length == new_length and original_self[old + 16:old + length]
                == wrapped[new + 16:new + length], 'NPDRM/capability metadata changed')
    digest = new_control[2][0]
    require(wrapped[digest + 36:digest + 56] == hashlib.sha1(elf).digest(),
            'SELF ELF digest mismatch')
    require(CONTENT.encode() in wrapped[:payload], 'Wrong NPJB00689 content ID')
    phoff = struct.unpack_from('>Q', elf, 32)[0]
    eoff, poff = struct.unpack_from('>QQ', wrapped, 0x30)
    require(wrapped[eoff:eoff + 64] == elf[:64]
            and wrapped[poff:poff + 56 * 8] == elf[phoff:phoff + 56 * 8],
            'SELF embedded headers differ')
    section = struct.unpack_from('>Q', wrapped, 0x48)[0]
    for i, row in enumerate(after):
        require(struct.unpack_from('>QQIIII', wrapped, section + i * 32)
                == (payload + row[2], row[5], 1, 0, 0, 2 if row[0] == 1 else 0),
                'SELF load-section mapping mismatch')
    return {'active_native_loads': 2, 'rx_rw_separated': True,
            'entry_tls_process_metadata_preserved': True,
            'original_bss_zero_filled': True, 'unrecorded_program_changes': False,
            'direct_hook_branches_checked': direct,
            'self_payload_and_load_mapping_verified': True,
            'npdrm_application_capability_content_identity_preserved': True}


def prepare(build, output, write=False):
    output = checked_output(output)
    build = Path(build).resolve()
    require((ROOT / 'work/builds').resolve() in build.parents, 'Build must be local')
    report = json.loads((build / 'BUILD_REPORT.json').read_text(encoding='utf8'))
    proof = json.loads((build / 'verification/RESULT.json').read_text(encoding='utf8'))
    match=re.fullmatch(r'rengoku_en_(\d{3})',build.name)
    require(match is not None,'Expected numbered Rengoku build')
    version=match[1]
    require(report['title_id'] == 'NPJB00689' and proof['all_passed'], 'Unverified build')
    tree = build / 'RPCS3/NPJB00689'
    require(file_inventory(tree) == report['game_files'], 'Build files changed')
    require(file_inventory(PKG) == report['source_files'], 'Original extraction changed')
    require(file_inventory(ROOT / 'localization') == report['locale_inputs'], 'Locales changed')
    overlay = build / 'PS3/NPJB00689'
    require(set(file_inventory(overlay)) == set(report['changed_files']), 'Wrong overlay inventory')
    require(all(identity(overlay / p) == report['game_files'][p]
                for p in report['changed_files']), 'Overlay differs from verified build')
    elf = (build / 'intermediate/EBOOT.ELF').read_bytes()
    wrapped = (overlay / 'USRDIR/EBOOT.BIN').read_bytes()
    require(sha(elf) == report['self']['elf_payload_sha256'], 'ELF differs from build')
    audit = audit_program((ROOT / 'work/eboot/EBOOT.ELF').read_bytes(), elf, wrapped,
                          (PKG / 'USRDIR/EBOOT.BIN').read_bytes(), report['runtime'])
    stage = build / 'verification/english_stage/STGZ3REN.SDAT.unedat'
    expected_stage = next(r['expected_sha256'] for r in proof['offline_decryption']
                          if r['case'] == 'english_stage' and r['accepted_and_byte_identical'])
    require(sha(stage.read_bytes()) == expected_stage and stage.read_bytes()[:4] == b'CPK ',
            'Verified installed stage plaintext unavailable')
    targets = {p: identity(stage if p == STAGE else overlay / p) for p in report['changed_files']}
    sources = {p: report['source_files'][p] for p in targets}
    original_stage = ROOT / 'work/story/STGZ3REN.cpk'
    sources[STAGE] = identity(original_stage)
    original_stage_proof = next(r for r in proof['offline_decryption'] if r['case'] == 'original_stage')
    require(sources[STAGE]['sha256'] == original_stage_proof['expected_sha256']
            and original_stage_proof['accepted_and_byte_identical'], 'Original installed stage mismatch')
    manifest = {'title_id': 'NPJB00689', 'content_id': CONTENT, 'local_build': build.name,
                'target': 'PS3 CFW hardware-test file overlay', 'package_format': 'overlay ZIP, not PKG',
                'build_report_sha256': identity(build / 'BUILD_REPORT.json')['sha256'],
                'source_files': sources, 'target_files': targets, 'executable_audit': audit,
                'stage_format': 'Verified post-install plaintext CPK, retains STGZ3REN.SDAT filename',
                'cfw_boot_tested': False, 'gameplay_tested': False, 'licenses_included': False}
    print('CFW target: /dev_hdd0/game/NPJB00689/; new local output:', output)
    print(json.dumps({'changed_files': targets, 'executable_audit': audit}, indent=2))
    if not write:
        print('DRY RUN: --write prepares a new overlay/ZIP only; no console or installation changes.')
        return manifest
    output.mkdir()
    for relative in targets:
        dest = output / 'NPJB00689' / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(stage if relative == STAGE else overlay / relative, dest)
    instructions = (ROOT / 'docs/CFW_HARDWARE_TEST.md').read_text(encoding='utf8').replace('018',version)
    (output / 'INSTALL.md').write_text(instructions, encoding='utf8')
    (output / 'BUILD-MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf8')
    require(file_inventory(output / 'NPJB00689') == targets, 'Hardware overlay readback mismatch')
    checks = ''.join('%s  NPJB00689/%s\n' % (v['sha256'], p) for p, v in sorted(targets.items()))
    checks += '%s  BUILD-MANIFEST.json\n' % identity(output / 'BUILD-MANIFEST.json')['sha256']
    checks += '%s  INSTALL.md\n' % identity(output / 'INSTALL.md')['sha256']
    (output / 'SHA256SUMS.txt').write_text(checks, encoding='utf8')
    archive = output / ('SRW-Z3-R-build%s-CFW-hardware-test1-overlay.zip'%version)
    members = ['NPJB00689/' + p for p in sorted(targets)] + ['INSTALL.md', 'BUILD-MANIFEST.json', 'SHA256SUMS.txt']
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name in members:
            z.write(output / name, name)
    with zipfile.ZipFile(archive) as z:
        require(z.testzip() is None and z.namelist() == members, 'ZIP inventory/CRC mismatch')
        for name in members:
            require(z.read(name) == (output / name).read_bytes(), 'ZIP payload differs')
    require(file_inventory(PKG) == report['source_files']
            and file_inventory(tree) == report['game_files'], 'Read-only inputs changed')
    evidence = {'overlay_and_zip_readbacks_passed': True, 'original_and_build_files_unchanged': True,
                'zip': identity(archive), 'zip_name': archive.name, 'game_files': len(targets),
                'executable_audit': audit, 'cfw_boot_tested': False, 'gameplay_tested': False}
    (output / 'VALIDATION.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf8')
    print('Prepared and verified CFW test overlay:', json.dumps(evidence, indent=2))
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    prepare(args.build, args.out, args.write)
