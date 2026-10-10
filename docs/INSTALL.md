# Installing the Rengoku-hen English patch

Current release **0.1.2** contains build **022** in a CFW debug PKG. Physical
PS3 boot and the corrected screens still need testing. The first public
release, 0.1.1, remains available.

Download [release 0.1.2](https://github.com/retro-trans/SRW-Z3-R/releases/tag/v0.1.2).
Choose the patch matching your complete source package:

| Source | Patch |
| --- | --- |
| Original Japanese NPJB00689 PKG | `SRW-Z3-R-NPJB00689-English-0.1.2-CFW-from-original.xdelta` |
| Exact English 0.1.1 PKG | `SRW-Z3-R-NPJB00689-English-0.1.1-to-0.1.2-CFW.xdelta` |

Both routes create the same English 0.1.2 PKG. Use a new output filename.
Full game packages, licenses and activation tools are not distributed.

## Retro Trans Automatic mode

1. Download [Retro Trans 0.5.1 or later](https://github.com/retro-trans/retro-trans-tools/releases/latest).
2. Refresh the catalog and browse to your original Japanese or exact English
   0.1.1 NPJB00689 `.pkg`.
3. Choose **Automatic**, then **Latest**, **Next** or **0.1.2**. Review the route.
4. Save to a new filename, such as `NPJB00689-English-0.1.2.pkg`.
5. Install the output using the CFW or RPCS3 instructions below.

Recognition checks the full size and hash; renaming the source is fine.
Extracted folders and installed game files are not compatible package sources.

## Retro Trans Apply xdelta mode

Download the matching `.xdelta` above. Select **Apply xdelta**, your source
PKG, that patch and a new `.pkg` output. This works offline. Check downloads
against `SHA256SUMS.txt` and identities against `BUILD-MANIFEST.json`.

## Delta Patcher

Use [Delta Patcher](https://github.com/marco-calautti/DeltaPatcher/releases/latest).
Select your source under **Original file** and its matching `.xdelta` under
**XDelta patch**. Enable **Backup original file** and keep **Checksum
validation** enabled, then apply. With backup enabled the result is
`<original-name>PATCHED.pkg` in the same folder. Without it, Delta Patcher
replaces the input, so retain an untouched original separately.

## xdelta command line

Use [xdelta3](https://github.com/jmacd/xdelta/releases/latest). From original:

```text
xdelta3 -d -s "NPJB00689-original.pkg" "SRW-Z3-R-NPJB00689-English-0.1.2-CFW-from-original.xdelta" "NPJB00689-English-0.1.2.pkg"
```

From exact English 0.1.1:

```text
xdelta3 -d -s "NPJB00689-English-0.1.1.pkg" "SRW-Z3-R-NPJB00689-English-0.1.1-to-0.1.2-CFW.xdelta" "NPJB00689-English-0.1.2.pkg"
```

Replace filenames with yours. On PowerShell use `./xdelta3.exe` if it is in
the current folder. Keep checksum verification enabled.

| Package | Bytes | SHA-256 |
| --- | ---: | --- |
| Original Japanese | 530,382,896 | `77431599e49115ee14070d11df910ea48d5f3c812883870d9770755d15400307` |
| English 0.1.1 | 721,946,688 | `dc570db31edda1928885ed5647e6a962f88e847eb309bcd2119978202ef39f3a` |
| English 0.1.2 | 621,868,688 | `2bcc308add953d165a2b00cb072bc317a19445e2e19786f64cb59ca39f988489` |

Check the output with `Get-FileHash -Algorithm SHA256 "NPJB00689-English-0.1.2.pkg"`.

## PS3 with CFW

Requires CFW supporting **debug PKG installation and fake/debug NPDRM SELF
loading**. This package is not Sony retail-signed. Stock firmware is unsupported;
no blanket HEN or firmware compatibility is claimed. Console installation and
boot remain untested.

1. Confirm your activated original NPJB00689 boots. Back up
   `/dev_hdd0/game/NPJB00689/` and savedata separately. Preserve licenses.
2. Verify the new PKG. Copy it to a FAT32 USB root or transfer to
   `/dev_hdd0/packages/` using your existing CFW setup. It is under 4 GiB.
3. Quit the game. In XMB **Package Manager > Install Package Files**, select
   the package. Menu wording varies by CFW. It replaces the same NPJB00689
   installation, rather than creating a second copy.
4. Launch from XMB with your matching original activation/license. Test a
   fresh boot and save/load in a separate slot.

Restore your backup or reinstall the original package to return to Japanese.
Preserve savedata and licenses. Do not delete this game's folder as a cache.

## RPCS3

Close RPCS3 and back up the installation and saves. Install with **File >
Install Packages/Raps/Edats**. Use your own matching license; no RAP is supplied.
The retained `DATA01.EDAT` requires your matching
`JP0700-NPJB00689_00-SRWZ3RENDLGPKG00.rap` in
`dev_hdd0/home/<active-user>/exdata/`. Error `80029521` indicates a missing
matching license.

Keep `dev_hdd0/game/NPJB00689`: it contains the digital game, not a disposable
disc cache. Preserve other games and savedata. A separate profile can retain
Japanese and English installations. Restart and load an in-game save;
emulator save states can retain old resources.

All 77 files matched after isolated native RPCS3 installation. The headless
installer then reported its known teardown assertion; file extraction passed,
but clean shutdown and gameplay are not claimed. See [validation notes](validation/0.1.2.md).

Report the release, RPCS3 or exact CFW version, affected screen/error code and
screenshot in a [GitHub issue](https://github.com/retro-trans/SRW-Z3-R/issues).
