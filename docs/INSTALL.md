# Installing the Rengoku-hen English patch

Current release **0.1.5** contains **build026**. The public output is RPCS3-only;
corrected screens still need gameplay testing. First public release 0.1.1
remains available.

Download [release 0.1.5](https://github.com/retro-trans/SRW-Z3-R/releases/tag/v0.1.5).

| Your source package | Patch |
| --- | --- |
| Original Japanese NPJB00689 PKG | `SRW-Z3-R-NPJB00689-English-0.1.5-RPCS3-from-original.xdelta` |
| Exact English public 0.1.2 PKG | `SRW-Z3-R-NPJB00689-English-0.1.2-to-0.1.5-RPCS3.xdelta` |

Both routes create the same English 0.1.5 PKG. Keep your source and save a new
output. Extracted folders and installed files are not whole-PKG patch inputs.

## Retro Trans

Use [Retro Trans 0.5.1 or later](https://github.com/retro-trans/retro-trans-tools/releases/latest).
Refresh the catalog, select your original Japanese or exact English 0.1.2 PKG,
open **Automatic**, then choose **Latest** or **0.1.5**. From 0.1.2, **Next** also
selects 0.1.5 after refresh. Version 0.1.1 can upgrade through 0.1.2.
Recognition uses the complete file size and SHA-256; renaming files is fine.

For offline use, select **Apply xdelta**, your source PKG, the matching patch
and a new `.pkg` output. Verify downloads against `SHA256SUMS.txt` and inputs
against `BUILD-MANIFEST.json`.

## DeltaPatcher

Use [DeltaPatcher](https://github.com/marco-calautti/DeltaPatcher/releases/latest).
Select your package under **Original file** and its matching **XDelta patch**.
Enable **Backup original file** and keep **Checksum validation** enabled.
Retain an untouched source package separately.

## xdelta command line

From the original Japanese package:

```text
xdelta3 -d -s "NPJB00689-original.pkg" "SRW-Z3-R-NPJB00689-English-0.1.5-RPCS3-from-original.xdelta" "NPJB00689-English-0.1.5.pkg"
```

From exact public English 0.1.2:

```text
xdelta3 -d -s "NPJB00689-English-0.1.2.pkg" "SRW-Z3-R-NPJB00689-English-0.1.2-to-0.1.5-RPCS3.xdelta" "NPJB00689-English-0.1.5.pkg"
```

Replace filenames with yours. In PowerShell use `./xdelta3.exe` for an executable
in the current folder. Keep checksum verification enabled.

- Original: **530,382,896 bytes**, SHA-256 `77431599e49115ee14070d11df910ea48d5f3c812883870d9770755d15400307`.
- Public English 0.1.2: **725,958,496 bytes**, SHA-256 `2beeb00d12be6df166893da1fa28baf8e9279793288c22da1a24c24dcf82a818`.
- English 0.1.5 output: **725,958,400 bytes**, SHA-256 `a9e00cbf97a2839cf34d8150b13989db4087bc6b7d9b4243c97823324591c570`.

## RPCS3 installation

Close RPCS3 and back up your installation and saves. Install the output with
**File > Install Packages/Raps/Edats**. Use your own matching original license;
no RAP is supplied. The retained DATA01.EDAT needs your matching activation.
Error 80029521 indicates a missing matching license.

Keep `dev_hdd0/game/NPJB00689`: it contains the digital game. Preserve savedata
and other games. Restart and load an in-game save; emulator save states can
retain older text/code. The title screen should show **v0.1.5** above
**github.com/retro-trans** in its lower-right corner.

## PS3 hardware and validation

This public package has cleared authentication and is for RPCS3. It is not a
Sony-signed or CFW/HEN installer. CFW packaging tools require private inputs;
full game packages and debug-PKG deltas are not distributed. Hardware boot and
gameplay remain untested. See [validation notes](validation/0.1.5.md).

All 77 files matched after isolated native installation. The known headless
teardown assertion is not a clean shutdown or game boot result.
