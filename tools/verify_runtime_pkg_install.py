"""Check RPCS3 package installation in a NEW isolated folder; preview first."""
import argparse,json,shutil,subprocess
from pathlib import Path
from apply_release import identity
from build_game import ROOT

def verify(package_dir,build,output,write=False):
    package_dir,build,output=[Path(p).resolve() for p in (package_dir,build,output)]
    output.relative_to((ROOT/'work').resolve())
    if output.exists():raise ValueError('Verification output must be new')
    proof=json.loads((package_dir/'PKG-VALIDATION.json').read_text(encoding='utf8'))
    packages=list(package_dir.glob('*.pkg'))
    if len(packages)!=1 or not proof['all_77_members_verified'] or identity(packages[0])!=proof['target']:
        raise ValueError('Unverified package')
    expected=dict(proof['files'])
    stage=build/'verification/english_stage/STGZ3REN.SDAT.unedat'
    expected['USRDIR/DATA_REN/STAGE/STGZ3REN.SDAT']=identity(stage)
    runtime=ROOT/'work/offline_rpcs3'
    print('Verify native install:',packages[0],flush=True)
    print('Isolated output:',output,'; 77 files, native SDAT decryption expected',flush=True)
    if not write:
        print('DRY RUN: original installation/saves/licenses untouched.');return
    output.mkdir();(output/'log').mkdir()
    for p in runtime.iterdir():
        if p.is_file() and p.suffix.lower() in ('.exe','.dll'):shutil.copyfile(p,output/p.name)
    shutil.copytree(runtime/'qt6',output/'qt6')
    run=subprocess.run([str(output/'rpcs3.exe'),'--headless','--installpkg',str(packages[0])],
        cwd=output,input=b'\n',capture_output=True,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
    (output/'install.log').write_bytes(run.stdout+run.stderr)
    installed=output/'dev_hdd0/game/NPJB00689'
    actual={p.relative_to(installed).as_posix():identity(p) for p in installed.rglob('*') if p.is_file()}
    result=dict(pkg=identity(packages[0]),rpcs3_exe=identity(output/'rpcs3.exe'),exit_code=run.returncode,
        installed_files=len(actual),all_77_game_files_match_build_with_native_sdat_decryption=actual==expected,
        isolated_install_only=True,gameplay_tested=False,ps3_hardware_tested=False)
    (output/'INSTALL-VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    if actual!=expected:raise ValueError('Installed member identities differ')
    print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--package-dir',type=Path,required=True)
    p.add_argument('--build',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--write',action='store_true');a=p.parse_args();verify(a.package_dir,a.build,a.out,a.write)
