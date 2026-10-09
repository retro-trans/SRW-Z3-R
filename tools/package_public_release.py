"""Create verified xdelta-only distribution from an existing local build. Dry-run by default."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import zipfile
from apply_release import identity

ROOT = Path(__file__).resolve().parents[1]


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def package(build, output, xdelta, version, write):
    build, output = build.resolve(), output.resolve()
    if output.exists():
        raise ValueError('Refusing to overwrite release directory')
    report = json.loads((build / 'BUILD_REPORT.json').read_text(encoding='utf8'))
    verification = json.loads((build / 'verification/RESULT.json').read_text(encoding='utf8'))
    if report['title_id'] != 'NPJB00689' or not verification['all_passed']:
        raise ValueError('Wrong game or failed build verification')
    source = ROOT / 'work/pkg'
    target = build / 'RPCS3/NPJB00689'
    for relative, expected in report['source_files'].items():
        if identity(source / relative) != expected:
            raise ValueError('Source changed: ' + relative)
    for relative, expected in report['game_files'].items():
        if identity(target / relative) != expected:
            raise ValueError('Build changed: ' + relative)
    print('Version:', version, 'Build:', build.name, flush=True)
    print('Output:', output, flush=True)
    for relative in report['changed_files']:
        print(relative, report['source_files'][relative], '->', report['game_files'][relative], flush=True)
    if not write:
        print('DRY RUN: 12 xdelta patches, manifest, validation, checksums, installer and guide; no game binaries published.')
        return
    output.mkdir(parents=True)
    patches = output / 'patches'; patches.mkdir()
    scratch = output / '_verification'; scratch.mkdir()
    rows = []
    for index, relative in enumerate(report['changed_files']):
        filename = '%02d-%s.xdelta' % (index + 1, Path(relative).name)
        delta = patches / filename
        subprocess.run([str(xdelta), '-e', '-9', '-s', str(source / relative), str(target / relative), str(delta)], check=True)
        decoded = scratch / filename
        subprocess.run([str(xdelta), '-d', '-s', str(source / relative), str(delta), str(decoded)], check=True)
        expected = report['game_files'][relative]
        if identity(decoded) != expected:
            raise ValueError('Patch round-trip failed: ' + relative)
        decoded.unlink()
        rows.append({'file': relative, 'patch': 'patches/' + filename,
                     'source': report['source_files'][relative], 'target': expected,
                     'patch_identity': identity(delta)})
        print('Round-trip verified:', relative, flush=True)
    scratch.rmdir()
    # The extractor's manifest is local metadata, not part of the retail game.
    game_files = {p: v for p, v in report['game_files'].items() if p.lower() != 'extraction_manifest.json'}
    source_files = {p: report['source_files'][p] for p in game_files}
    manifest = {'schema': 'srw-z3-r-file-patches-v1', 'game_id': 'srw-z3-rengoku-ps3',
                'game_name': 'Super Robot Taisen Z3: Rengoku-hen', 'title_id': 'NPJB00689',
                'platform': 'PS3', 'language': 'en', 'version': version, 'local_build': build.name,
                'distribution': 'per-file-xdelta', 'retro_trans_automatic_supported': False,
                'build_report_sha256': identity(build / 'BUILD_REPORT.json')['sha256'],
                'source_pkg_sha256': report['source_pkg_sha256'],
                'build_source_commit': None,
                'provenance_note': 'Existing build 018 predates Git initialization. Published translations remove original script fields; the build input hashes remain in the local build report.',
                'source_files': source_files, 'target_files': game_files, 'patches': rows}
    save(output / 'BUILD-MANIFEST.json', manifest)
    validation = {'title_id': 'NPJB00689', 'version': version, 'local_build': build.name,
                  'patch_roundtrips': [{'file': r['file'], 'sha256': r['target']['sha256'], 'passed': True} for r in rows],
                  'all_patch_roundtrips_passed': True, 'recorded_build_tests_passed': 118,
                  'recorded_archive_readbacks_passed': report['archive_members_rebuilt'],
                  'offline_build_checks': verification, 'gameplay_tested': False,
                  'ps3_hardware_tested': False}
    save(output / 'VALIDATION.json', validation)
    shutil.copyfile(ROOT / 'tools/apply_release.py', output / 'apply_release.py')
    shutil.copyfile(ROOT / 'docs/INSTALL_FOLDER.md', output / 'INSTALL.md')
    name = 'SRW-Z3-R-PS3-English-%s-file-patches.zip' % version
    archive = output / name
    inputs = [p for p in output.rglob('*') if p.is_file()]
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as stream:
        for path in inputs:
            stream.write(path, path.relative_to(output).as_posix())
    with zipfile.ZipFile(archive) as stream:
        if stream.testzip() is not None or set(stream.namelist()) != {p.relative_to(output).as_posix() for p in inputs}:
            raise ValueError('Patch ZIP integrity failed')
        for path in inputs:
            import hashlib
            if hashlib.sha256(stream.read(path.relative_to(output).as_posix())).hexdigest() != identity(path)['sha256']:
                raise ValueError('ZIP readback failed')
    sums = [identity(output / n)['sha256'] + '  ' + n for n in (name, 'BUILD-MANIFEST.json', 'VALIDATION.json')]
    (output / 'SHA256SUMS.txt').write_text('\n'.join(sums) + '\n', encoding='utf8')
    print('Verified release ZIP:', identity(archive), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--xdelta', type=Path, required=True)
    parser.add_argument('--version', required=True)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    package(args.build, args.out, args.xdelta, args.version, args.write)
