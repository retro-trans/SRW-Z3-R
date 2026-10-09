"""Package a verified RPCS3 PKG as a standard Retro Trans release; preview first.

Requires a current checkout/installation of retro-trans-tools. Full game PKGs
remain local. Only xdelta and protocol JSON/checksums are release assets.
"""
import argparse
import json
from pathlib import Path
import re
import sys

from apply_release import identity

ROOT = Path(__file__).resolve().parents[1]


def prepare(args):
    output = args.out.resolve()
    output.relative_to((ROOT / 'work').resolve())
    if output.exists():
        raise ValueError('Release output must be NEW')
    if not re.fullmatch('[0-9a-f]{40}', args.source_commit):
        raise ValueError('Supply the full public packaging/source commit')
    if not re.fullmatch(r'\d+\.\d+\.\d+', args.version):
        raise ValueError('Supply a numeric release version')
    proof = json.loads(args.target_validation.read_text(encoding='utf8'))
    runtime = json.loads(args.runtime_validation.read_text(encoding='utf8'))
    source, target = identity(args.pkg), identity(args.target)
    if source != proof['original'] or target != proof['target'] or target != runtime['pkg']:
        raise ValueError('Verified package identities changed')
    if not proof['all_77_members_verified'] or not runtime[
            'all_77_game_files_match_build018_with_native_sdat_decryption']:
        raise ValueError('Complete package/RPCS3 installation checks required')
    config = dict(game_id='srw-z3-rengoku-ps3',
                  game_name='Super Robot Taisen Z3: Rengoku-hen', platform='PS3',
                  version=args.version, source_commit=args.source_commit,
                  patches=[dict(patch='SRW-Z3-R-NPJB00689-English-%s-RPCS3.xdelta' % args.version,
                                edition='Japanese digital NPJB00689 (RPCS3 package)',
                                language='en', source_version='original',
                                source_format='pkg', target_format='pkg',
                                source=str(args.pkg.resolve()), target=str(args.target.resolve()))])
    print('Original:', source, '\nTarget:', target, flush=True)
    print('Standard manifest v1; original PKG -> new RPCS3-only PKG.', flush=True)
    print('Source/packaging commit:', args.source_commit, flush=True)
    print('Output:', output, flush=True)
    if not args.write:
        print('DRY RUN: build one bare xdelta, BUILD-MANIFEST.json, VALIDATION.json, SHA256SUMS.txt.')
        return
    if args.retro_tools:
        sys.path.insert(0, str(args.retro_tools.resolve()))
    from retro_trans.release import build_release, validate_directory
    config_path = output.parent / (output.name + '-private-config.json')
    with config_path.open('x', encoding='utf8') as stream:
        json.dump(config, stream, indent=2)
    manifest = build_release(config_path, output, cache=ROOT / 'work/retro_release_cache')
    validate_directory(output)
    print('Standard release verified:', json.dumps(manifest, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pkg', type=Path, required=True)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--target-validation', type=Path, required=True)
    parser.add_argument('--runtime-validation', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    parser.add_argument('--version', required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--retro-tools', type=Path)
    parser.add_argument('--write', action='store_true')
    prepare(parser.parse_args())
