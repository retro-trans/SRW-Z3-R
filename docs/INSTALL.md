# Installing the Rengoku-hen English patch

The first public release, **0.1.1**, uses Retro Trans's standard single-file xdelta format.
Input: your original Japanese **PS3 NPJB00689 PKG**.
Output: a new English PKG for **RPCS3**, containing build 018's translation.
No Python or separate xdelta installation is needed when using the Windows app.

## Retro Trans Automatic mode

1. Download [Retro Trans 0.5.1 or later](https://github.com/retro-trans/retro-trans-tools/releases/latest).
2. Refresh its patch catalog and browse to your original NPJB00689 `.pkg`.
3. Choose **Automatic**, then **Latest** or **0.1.1**. Review the route.
4. Choose a new output name, such as `NPJB00689-English-0.1.1.pkg`, and click Patch.
5. Close RPCS3 and keep your existing game and saves backed up. In RPCS3, choose
   **File > Install Packages/Raps/Edats** and install the generated package in
   your intended RPCS3 profile. The patcher itself does not install games.

Recognition checks all original bytes; renaming the file is fine. The source
must be 530,382,896 bytes with SHA-256
`77431599e49115ee14070d11df910ea48d5f3c812883870d9770755d15400307`.
Other packages, Jigoku-hen, extracted folders and the old English folder are
not compatible sources for this route. Use the `.pkg` output format.

Retro Trans's general PS3 installation-data reminder concerns disc caches.
**Do not delete `dev_hdd0/game/NPJB00689` as a cache**: this is the installed
digital game. Keep savedata, licenses and other games. Use a separate RPCS3
profile if you want to retain the Japanese and English installations separately.

## Retro Trans Apply xdelta mode

Download `SRW-Z3-R-NPJB00689-English-0.1.1-RPCS3.xdelta` from
[release 0.1.1](https://github.com/retro-trans/SRW-Z3-R/releases/tag/v0.1.1).
Choose Apply xdelta, the matching original PKG, that local patch, and a new
`.pkg` output. This mode works offline but does not provide catalog recognition.
Compare your source and output against `BUILD-MANIFEST.json` and verify the
patch download against `SHA256SUMS.txt`.

## Delta Patcher

Download [Delta Patcher](https://github.com/marco-calautti/DeltaPatcher/releases/latest)
and the `.xdelta` asset from [release 0.1.1](https://github.com/retro-trans/SRW-Z3-R/releases/tag/v0.1.1).

1. Under **Original file**, select your matching Japanese NPJB00689 `.pkg`.
2. Under **XDelta patch**, select
   `SRW-Z3-R-NPJB00689-English-0.1.1-RPCS3.xdelta`.
3. In the patch options, enable **Backup original file** and keep
   **Checksum validation** enabled, then click **Apply patch**.
4. With backup enabled, the output is named `<original-name>PATCHED.pkg` in
   the same folder. Install that English package through RPCS3.

Without Backup original file enabled, Delta Patcher replaces the input file.
Use a separate copy of your original PKG if you prefer.

## xdelta command line

Download [xdelta3](https://github.com/jmacd/xdelta/releases/latest) and the same
`.xdelta` asset. Run this in a folder containing the patch and your original
package; replace `NPJB00689-original.pkg` with your original filename:

```sh
xdelta3 -d -s "NPJB00689-original.pkg" "SRW-Z3-R-NPJB00689-English-0.1.1-RPCS3.xdelta" "NPJB00689-English-0.1.1.pkg"
```

`-d` decodes the patch, and `-s` selects the original package. Use a new output
filename. On Windows PowerShell, use `./xdelta3.exe` instead of `xdelta3` if
its executable is in the current folder. Install the resulting English PKG
through RPCS3.

For either manual method, check the original identity listed above and the
patch's `SHA256SUMS.txt`. The expected output is **721,946,688 bytes**, SHA-256
`dc570db31edda1928885ed5647e6a962f88e847eb309bcd2119978202ef39f3a`.
You can check it in PowerShell with:

```powershell
Get-FileHash -Algorithm SHA256 "NPJB00689-English-0.1.1.pkg"
```

Use the actual output filename when checking a Delta Patcher result.

## Compatibility and license

The output is a modified retail-style package with cleared authentication
blocks, intended for RPCS3. It is **not Sony-signed and is not advertised as a
PS3/CFW/HEN package installer**. The fake SELF executable and translated assets
use verified local build 018 content; package installation
natively decrypts its stage SDAT. Gameplay and physical-console checks remain
pending. See the [release notes](releases/0.1.1.md) for validation limits.

Keep your own matching game activation/license setup. No RAP is included.
The original `DATA01.EDAT` requires your matching
`JP0700-NPJB00689_00-SRWZ3RENDLGPKG00.rap` in RPCS3's
`dev_hdd0/home/<active-user>/exdata/`. Error `80029521` indicates a missing
matching license. Restart the game and load an in-game save when testing;
emulator save states can retain earlier code or resources.

Report the release version, RPCS3 version, affected screen and screenshot in a
[GitHub issue](https://github.com/retro-trans/SRW-Z3-R/issues).
