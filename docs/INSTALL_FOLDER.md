# Installing the Rengoku-hen English patch

Download the patch ZIP from [GitHub Releases](https://github.com/retro-trans/SRW-Z3-R/releases).
Use your own pristine **PS3 NPJB00689** game folder extracted from the matching
Japanese Rengoku-hen package. The folder must contain `PARAM.SFO` and `USRDIR`.
These patches do not accept Jigoku-hen BLJS10256 or an already translated build.

## Apply the patch

1. Extract the release ZIP into a separate folder.
2. Install Python 3.8 or later and [xdelta3](https://github.com/jmacd/xdelta-gpl/releases).
3. Close RPCS3 and keep your original game folder and saves backed up.
4. Preview installation from the extracted patch folder:

```powershell
python apply_release.py --source "D:/Games/NPJB00689-original" --out "D:/Games/NPJB00689-English" --xdelta "D:/Tools/xdelta3.exe"
```

5. After all input hashes pass, repeat with `--write`:

```powershell
python apply_release.py --source "D:/Games/NPJB00689-original" --out "D:/Games/NPJB00689-English" --xdelta "D:/Tools/xdelta3.exe" --write
```

The installer creates a new complete game folder, applies the per-file patches,
and verifies every target game file. Choose a new output folder outside the
original. If verification fails, check `BUILD-MANIFEST.json` for the exact
expected file sizes and SHA-256 hashes. Keep checksum verification enabled.

Download integrity is recorded in `SHA256SUMS.txt`. The ZIP contains xdelta
patches, the installer, manifest, validation record and this guide. GitHub's
**Source code (zip)** contains project sources; download the release patch ZIP
to translate the game. This directory patch set is not compatible with
Retro Trans's whole-image Automatic mode.

## RPCS3

Choose **File > Boot Game** and select the new English folder. Keep your own
matching game activation/license setup. The patch does not contain a RAP.
The original `DATA01.EDAT` requires your own matching
`JP0700-NPJB00689_00-SRWZ3RENDLGPKG00.rap` in RPCS3's
`dev_hdd0/home/<active-user>/exdata/`. Error `80029521` indicates a missing
matching license. Restart the game and load an in-game save when testing;
emulator save states can retain earlier code or resources.

## Physical PS3

The output uses a fake SELF executable and requires compatible modified
firmware and the matching original NPJB00689 installation/activation.
With the game closed, back up the installation, then copy the twelve files
listed in the manifest's `patches` array from the English output to the matching
paths under `/dev_hdd0/game/NPJB00689/`. Keep savedata separate.
Physical PS3 execution and blanket CFW/HEN compatibility remain unverified.
Stock firmware is not supported by this test executable.

## Report a problem

Include the release version, RPCS3 version or console setup, the affected
screen and a screenshot in a [GitHub issue](https://github.com/retro-trans/SRW-Z3-R/issues).
Build 018 has passing asset, patch and offline format checks; its new layouts
still need gameplay confirmation. See each release's notes for coverage.
