"""Verify CFW debug PKG in a NEW isolated RPCS3 installation; preview by default.

This checks a native independent package parser/installer, not PS3 hardware.
No firmware, licenses, original user game or saves are copied/changed.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

from apply_release import identity
from build_game import ROOT
from rengoku_runtime import require


def verify(package_dir, output, write=False):
    package_dir, output = Path(package_dir).resolve(), Path(output).resolve()
    require((ROOT / 'work').resolve() in output.parents and not output.exists(),
            'Verification output must be new and under work')
    proof = json.loads((package_dir / 'PKG-VALIDATION.json').read_text(encoding='utf8'))
    require(proof['all_77_members_verified'] and proof['debug_authentication_verified'],
            'Unverified CFW PKG')
    pkg = package_dir / proof.get('package_name','SRW-Z3-R-NPJB00689-English-build018-CFW-test1.pkg')
    require(pkg.parent==package_dir,'Package name must stay within the prepared output')
    require(identity(pkg) == proof['package'], 'Package changed')
    runtime = ROOT / 'work/offline_rpcs3'
    print('New isolated verification:', output, flush=True)
    print('Native-install all 77 files from:', pkg, flush=True)
    if not write:
        print('DRY RUN: --write copies offline program only; no hardware/installed user games.')
        return
    output.mkdir()
    (output / 'log').mkdir()
    for p in runtime.iterdir():
        if p.is_file() and p.suffix.lower() in ('.exe', '.dll'):
            shutil.copyfile(p, output / p.name)
    shutil.copytree(runtime / 'qt6', output / 'qt6')
    process = subprocess.run([str(output / 'rpcs3.exe'), '--headless', '--installpkg', str(pkg)],
        cwd=output, input=b'\n', capture_output=True, timeout=180,
        creationflags=subprocess.CREATE_NO_WINDOW)
    (output / 'install.log').write_bytes(process.stdout + process.stderr)
    installed = output / 'dev_hdd0/game/NPJB00689'
    actual = {p.relative_to(installed).as_posix(): identity(p)
              for p in installed.rglob('*') if p.is_file()}
    result = dict(package=identity(pkg), rpcs3=identity(output / 'rpcs3.exe'),
                  exit_code=process.returncode, installed_files=len(actual),
                  all_77_game_files_match_cfw_pkg=actual == proof['files'],
                  isolated_install_only=True, ps3_hardware_install_tested=False,
                  ps3_hardware_boot_tested=False, gameplay_tested=False)
    (output / 'INSTALL-VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    require(result['all_77_game_files_match_cfw_pkg'], 'Native package extraction differs')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args()
    verify(a.package_dir, a.out, a.write)
