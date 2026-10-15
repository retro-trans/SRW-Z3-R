"""Number complete builds and keep their in-game version in sync."""
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def version_key(value):
    if not isinstance(value, str) or not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', value):
        raise ValueError('Invalid build version: ' + str(value))
    return tuple(map(int, value.split('.')))


def next_version(root=ROOT, requested_version=None):
    state = json.loads((Path(root) / 'build_version.json').read_text(encoding='utf8'))
    major, minor, patch = version_key(state['last_successful_build'])
    if requested_version is not None:
        if version_key(requested_version) <= (major, minor, patch):
            raise ValueError('Requested version must be newer than the last complete build')
        return requested_version
    return '%d.%d.%d' % (major, minor, patch + 1)


def write_json(path, data):
    temporary = path.with_name(path.name + '.tmp')
    try:
        with temporary.open('x', encoding='utf8', newline='\n') as stream:
            stream.write(json.dumps(data, indent=2) + '\n')
        os.replace(str(temporary), str(path))
    finally:
        if temporary.exists():
            temporary.unlink()


def stamp(outdir, report, expected_version, root=ROOT, requested_version=None):
    if (report.get('version') != expected_version or report.get('title_footer_version') != expected_version
            or report.get('pending') or not report.get('archive_readback_verified')
            or not report.get('sdat_roundtrip_verified') or not report.get('source_files_preserved')
            or not report.get('catalogs_preserved') or not report.get('game_files')
            or not report.get('patch_zip') or not report.get('title_footer', {}).get('verified')):
        raise ValueError('Refusing to number a build without completed insertion and footer verification')
    root, outdir = Path(root), Path(outdir)
    lock = root / 'build_version.lock'
    with lock.open('x'):
        pass
    try:
        if next_version(root, requested_version) != expected_version:
            raise ValueError('Build counter changed; rebuild with the current title version')
        manifest = outdir / 'build_manifest.json'
        if manifest.exists():
            raise ValueError('Existing build stamp cannot be replaced')
        write_json(manifest, dict(schema=1, version=expected_version,
            local_build=outdir.name, title_footer_version=expected_version,
            title_footer_credit=report['title_footer']['credit'],
            verified=True, files=report['game_files'], patch_zip=report['patch_zip']))
        try:
            write_json(root / 'build_version.json', dict(schema=1, last_successful_build=expected_version,
                local_build=outdir.name, note='Advance only after complete build/readback and matching title-footer verification.'))
        except BaseException:
            manifest.unlink()
            raise
    finally:
        lock.unlink()
    return expected_version
