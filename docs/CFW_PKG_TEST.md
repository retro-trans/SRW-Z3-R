# Rengoku-hen build 018 — CFW PKG test 1

This complete English **NPJB00689** package is for a PS3 with CFW supporting
debug PKG installation and fake/debug NPDRM SELF loading. It has not yet been
installed or booted on a physical PS3. It is a local test, not the public
RPCS3-only release PKG. It retains the original content identity and encrypted
DATA01.EDAT; your matching original activation/license is required.

## Install

1. Confirm your original activated Japanese NPJB00689 starts on the console.
   Back up `/dev_hdd0/game/NPJB00689/` before replacing its installed files.
   Back up savedata separately and keep activation/license files unchanged.
2. Check the package against SHA256SUMS.txt. Copy the `.pkg` to the root of a
   FAT32 USB device, or transfer it to `/dev_hdd0/packages/` using your existing
   CFW file manager/FTP setup. It is smaller than FAT32's 4 GiB file limit.
3. Quit the game. In XMB **Package Manager → Install Package Files**, select
   the package from your USB device or internal package directory. Menu wording
   varies by CFW. This installs over the same NPJB00689 game, not a second copy.
4. Launch the installed English game from the XMB. Keep your original matching
   license; this package contains no RAP/RIF, act.dat or activation tools.

The package includes all 77 game files. Its NPDRM executable is byte-identical
to the audited CFW overlay. The verified installed plaintext story archive
retains its `.SDAT` filename and is packaged as ordinary data, avoiding a
second installer decryption. Debug package authentication is generated anew;
the modified package is not Sony retail-signed or intended for stock firmware.

## Test and restore

All 77 files were independently checked after native RPCS3 package installation.
The installer logged success, then the headless process returned its known
shutdown assertion (3221226505). File extraction passed; this is not a clean
process-exit, gameplay or physical-console installation result. Container
authentication also matches a synthetic package from the upstream PSL1GHT
writer at commit f649a08fd536a9e27c08c7db2d93a2d7ee4c3bbe.

Check startup/title, New Game, opening narration, Episode 1 dialogue/Back Log,
unit/pilot stats, terrain labels, Spirit commands, a battle/subtitle, results,
Intermission and save/load in a separate slot. Translation/layout limitations
of build 018 remain. Report console model, exact CFW version, installation or
launch error code, and last working screen. Offline file checks and emulator
installation do not establish physical-console compatibility.

To restore, quit the game and restore the backed-up original game folder, or
reinstall your original unmodified package. Preserve savedata and licenses.
Do not delete this digital game's installed folder as a cache-cleaning step.

Container format references: [PSL1GHT package writer](https://github.com/ps3dev/PSL1GHT/blob/master/tools/ps3py/pkg.py)
and [RPCS3 package reader](https://github.com/RPCS3/rpcs3/blob/master/rpcs3/Crypto/unpkg.cpp).
