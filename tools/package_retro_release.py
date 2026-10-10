"""Package a verified RPCS3 or CFW PKG as a standard release; preview first.

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
    cfw = proof.get('format') == 'CFW debug PKG (not retail-signed)'
    if cfw:
        raise ValueError('Debug PKG encryption prevents source reuse: a whole-PKG xdelta embeds the complete game. Keep CFW packages local; publish RPCS3 deltas.')
    verified_target = proof.get('package') if cfw else proof.get('target')
    installed_target = runtime.get('package') if cfw else runtime.get('pkg')
    if source != proof['original'] or target != verified_target or target != installed_target:
        raise ValueError('Verified package identities changed')
    package_ok = proof.get('all_77_members_verified')
    if cfw:
        package_ok = package_ok and proof.get('full_cipher_roundtrip') and proof.get('debug_authentication_verified')
    install_ok = runtime.get('all_77_game_files_match_cfw_pkg') if cfw else runtime.get(
        'all_77_game_files_match_build_with_native_sdat_decryption', runtime.get(
        'all_77_game_files_match_build018_with_native_sdat_decryption'))
    if not package_ok or not install_ok:
        raise ValueError('Complete package/RPCS3 installation checks required')
    suffix = 'CFW' if cfw else 'RPCS3'
    # Edition is part of Retro Trans's graph identity. Keep the first release's
    # label so original/0.1.1 recognition reaches 0.1.2 without ambiguity.
    edition = 'Japanese digital NPJB00689 (RPCS3 package)'
    config = dict(game_id='srw-z3-rengoku-ps3',
                  game_name='Super Robot Taisen Z3: Rengoku-hen', platform='PS3',
                  version=args.version, source_commit=args.source_commit,
                  patches=[dict(patch='SRW-Z3-R-NPJB00689-English-%s-%s-from-original.xdelta' % (args.version, suffix),
                                edition=edition,
                                language='en', source_version='original',
                                source_format='pkg', target_format='pkg',
                                source=str(args.pkg.resolve()), target=str(args.target.resolve()))])
    print('Original:', source, '\nTarget:', target, flush=True)
    if args.previous:
        if not args.previous_manifest:
            raise ValueError('A previous package requires its published manifest')
        previous_manifest = json.loads(args.previous_manifest.read_text(encoding='utf8'))
        previous_version = previous_manifest['version']
        if not re.fullmatch(r'\d+\.\d+\.\d+', previous_version) or previous_version == args.version:
            raise ValueError('Invalid previous release version')
        previous = identity(args.previous)
        if not any(previous == dict(bytes=p['target_bytes'], sha256=p['target_sha256'])
                   for p in previous_manifest['patches']):
            raise ValueError('Previous package does not match the published manifest')
        config['patches'].append(dict(
            patch='SRW-Z3-R-NPJB00689-English-%s-to-%s-%s.xdelta' % (previous_version, args.version, suffix),
            edition=edition,
            language='en', source_version=previous_version, source_format='pkg', target_format='pkg',
            source=str(args.previous.resolve()), target=str(args.target.resolve())))
        print('Upgrade from published', previous_version, ':', previous, flush=True)
    print('Standard manifest v1; verified inputs -> new %s PKG.' % suffix, flush=True)
    print('Source/packaging commit:', args.source_commit, flush=True)
    print('Output:', output, flush=True)
    if not args.write:
        print('DRY RUN: build %d bare xdelta(s), manifest, validation and checksums.' % len(config['patches']))
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
    parser.add_argument('--previous', type=Path)
    parser.add_argument('--previous-manifest', type=Path)
    parser.add_argument('--write', action='store_true')
    prepare(parser.parse_args())
