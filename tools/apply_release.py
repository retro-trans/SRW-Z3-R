"""Apply a Rengoku per-file xdelta release to a new folder; dry-run by default."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess


def identity(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return {'bytes': path.stat().st_size, 'sha256': digest.hexdigest()}


def inside(root, relative):
    path = PurePosixPath(relative)
    if path.is_absolute() or not path.parts or any(p in ('..', '.') or ':' in p or '\\' in p for p in path.parts):
        raise ValueError('Unsafe manifest path: ' + relative)
    result = root.joinpath(*path.parts)
    if root.resolve() not in result.resolve().parents:
        raise ValueError('Path escapes folder: ' + relative)
    return result


def apply(bundle, source, output, xdelta, write=False):
    bundle, source, output = bundle.resolve(), source.resolve(), output.resolve()
    manifest = json.loads((bundle / 'BUILD-MANIFEST.json').read_text(encoding='utf8'))
    if manifest['schema'] != 'srw-z3-r-file-patches-v1' or manifest['title_id'] != 'NPJB00689':
        raise ValueError('Unsupported release or game')
    if output.exists() or output == source or source in output.parents or output in source.parents:
        raise ValueError('Choose a new output folder outside the source tree')
    if not source.is_dir():
        raise ValueError('Source must be the original extracted NPJB00689 game folder')
    if any(p.is_symlink() for p in source.rglob('*')):
        raise ValueError('Source folder must not contain symlinks')
    # Check every game file before creating the output, including unchanged assets.
    for relative, expected in manifest['source_files'].items():
        path = inside(source, relative)
        if not path.is_file() or identity(path) != expected:
            raise ValueError('Original input mismatch: ' + relative)
    for row in manifest['patches']:
        path = inside(bundle, row['patch'])
        if not path.is_file() or identity(path) != row['patch_identity']:
            raise ValueError('Patch download mismatch: ' + row['patch'])
    print('Verified original NPJB00689 files and all %d patches.' % len(manifest['patches']), flush=True)
    print('New output:', output, flush=True)
    if not write:
        print('DRY RUN: add --write to copy and patch the game folder.')
        return
    binary = shutil.which(xdelta) or (str(Path(xdelta).resolve()) if Path(xdelta).is_file() else None)
    if not binary:
        raise ValueError('Install xdelta3 or pass --xdelta /path/to/xdelta3')
    shutil.copytree(source, output)
    for row in manifest['patches']:
        dest = inside(output, row['file'])
        temporary = dest.with_name(dest.name + '.xdelta-output')
        if temporary.exists():
            raise ValueError('Unexpected temporary file already exists')
        subprocess.run([binary, '-d', '-s', str(inside(source, row['file'])),
                        str(inside(bundle, row['patch'])), str(temporary)], check=True)
        if identity(temporary) != row['target']:
            raise ValueError('Decoded output mismatch: ' + row['file'])
        temporary.replace(dest)
        print('Verified:', row['file'], flush=True)
    for relative, expected in manifest['target_files'].items():
        if identity(inside(output, relative)) != expected:
            raise ValueError('Final game file mismatch: ' + relative)
    print('All target game files verified. Boot this new folder in RPCS3.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--xdelta', default='xdelta3')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    apply(args.bundle, args.source, args.out, args.xdelta, args.write)
