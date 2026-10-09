"""Verify a completed local build, with optional offline RPCS3 decrypt checks.

Read-only by default. --write creates a NEW verification directory inside the
build and uses the prepared offline RPCS3 as a format checker, without booting
a game, installing files, or reading/writing user saves.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

from build_game import ROOT, PKG, document, file_inventory
from rengoku_runtime import require, sha


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('build',type=Path)
    ap.add_argument('--write',action='store_true')
    args=ap.parse_args();root=args.build.resolve()
    require((ROOT/'work/builds').resolve() in root.parents,'Build must be under work/builds')
    report=json.loads((root/'BUILD_REPORT.json').read_text(encoding='utf-8'))
    require(report['title_id']=='NPJB00689','Wrong title')
    require(file_inventory(root/'RPCS3/NPJB00689')==report['game_files'],'Complete game folder hash mismatch')
    require(file_inventory(PKG)==report['source_files'],'Original extracted assets changed')
    require(file_inventory(ROOT/'localization')==report['locale_inputs'],'Canonical localization changed since build')
    overlay=file_inventory(root/'PS3/NPJB00689')
    require(set(overlay)==set(report['changed_files']),'Overlay file inventory mismatch')
    require(all(overlay[p]==report['game_files'][p] for p in overlay),'PS3/RPCS3 assets differ')
    archive=root/report['patch_zip']['name']
    require(sha(archive.read_bytes())==report['patch_zip']['sha256'],'Patch archive hash mismatch')
    with zipfile.ZipFile(archive) as z:
        require(z.testzip() is None,'ZIP CRC mismatch')
        for p in overlay:require(sha(z.read('NPJB00689/'+p))==overlay[p]['sha256'],'ZIP payload differs')
    print('Complete folder, PS3 overlay and ZIP hashes agree. Original assets and catalogs are unchanged.',flush=True)
    verification=root/'verification'
    require(not verification.exists(),'Verification output exists; refusing overwrite')
    stage=root/'RPCS3/NPJB00689/USRDIR/DATA_REN/STAGE/STGZ3REN.SDAT'
    plain_candidates=list((root/'intermediate').glob('archive_*/rebuilt.cpk'))
    stage_plain=next(p for p in plain_candidates if (p.parent/'STGZ3REN.SDAT').exists())
    cases=[('original_stage',PKG/'USRDIR/DATA_REN/STAGE/STGZ3REN.SDAT',ROOT/'work/story/STGZ3REN.cpk'),
           ('english_stage',stage,stage_plain),
           ('english_executable',root/'RPCS3/NPJB00689/USRDIR/EBOOT.BIN',root/'intermediate/EBOOT.ELF')]
    for name,source,expected in cases:print('Offline decrypt check:',name,source.name,'-> SHA256',sha(expected.read_bytes()))
    if not args.write:
        print('DRY RUN; --write creates verification copies and runs the offline format checks. No game is booted.')
        return
    verification.mkdir();results=[]
    for name,source,expected in cases:
        dest=verification/name;dest.mkdir();target=dest/source.name;shutil.copyfile(source,target)
        print('Checking with RPCS3:',name,flush=True)
        runtime=ROOT/'work/offline_rpcs3'
        try:
            process=subprocess.run([str(runtime/'rpcs3.exe'),'--headless','--decrypt',str(target)],cwd=runtime,
                 input=b'\n',capture_output=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
            output=process.stdout+process.stderr;code=process.returncode
        except subprocess.TimeoutExpired as error:
            output=(error.stdout or b'')+(error.stderr or b'');code='timeout'
        (dest/'decrypt.log').write_bytes(output)
        expected_sha=sha(expected.read_bytes())
        matches=[p for p in dest.iterdir() if p.is_file() and p.name not in (source.name,'decrypt.log') and sha(p.read_bytes())==expected_sha]
        result={'case':name,'exit_code':code,'accepted_and_byte_identical':bool(matches),'expected_sha256':expected_sha,
                'output_files':[p.name for p in matches]}
        results.append(result)
        print(document(result),flush=True)
    status={'title_id':'NPJB00689','offline_decryption':results,
            'all_passed':all(r['accepted_and_byte_identical'] for r in results),
            'complete_game_overlay_zip_hashes_agree':True,'source_assets_and_catalogs_unchanged':True,
            'gameplay_tested':False,'ps3_hardware_tested':False}
    (verification/'RESULT.json').write_text(document(status),encoding='utf-8')
    require(status['all_passed'],'Offline acceptance check failed; inspect local verification logs')


if __name__=='__main__':main()
