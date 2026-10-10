# Rengoku-hen build 018 — CFW hardware test 1

Target: **PS3 with CFW**, Japanese digital game **NPJB00689**. This is a local
hardware-test file overlay. It has passed file/executable checks but has not
been booted on a physical console. It is not the RPCS3 release PKG or a new PKG
installer. Your CFW must support NPDRM fake/debug SELF loading.

## Install

1. Install and activate your own original Japanese NPJB00689 game on the PS3.
   Confirm it starts before applying this test. Keep its existing license;
   no RAP/RIF or activation file is included here.
2. Quit the game. Using your CFW file manager or FTP, back up the installed
   `/dev_hdd0/game/NPJB00689/` folder to your computer or another safe location.
   Keep savedata and the existing game folder. Do not delete it as a cache.
3. Extract this ZIP on your computer. Copy the **contents of `NPJB00689`**
   into `/dev_hdd0/game/NPJB00689/`, merging the folders and replacing the
   twelve matching files. Do not nest a second NPJB00689 folder in the game.
   Do not copy INSTALL.md, BUILD-MANIFEST.json or SHA256SUMS.txt into the game.
4. Download/read back the twelve transferred files and check their SHA-256
   values against `BUILD-MANIFEST.json` or `SHA256SUMS.txt`. All other original
   game files remain in place. Launch the installed game from the XMB.

The executable retains NPJB00689 application, content and capability metadata,
with separate executable/read-write segments and the verified English payload.
The story archive is supplied in its verified post-install plaintext form,
under its original `STGZ3REN.SDAT` filename. File copying does not run the
package installer's decryption step. Other translated files match build 018.

## Test and report

Check startup and title/menu transitions, New Game, opening narration,
Episode 1, dialogue/Back Log, unit/pilot stats, terrain labels, Spirit commands,
one battle animation/subtitle, the battle result, and Intermission. Test
save/load using a separate save slot. Existing review and unfinished artwork
and longer-subtitle work are unchanged from build 018.

Report your console model, exact CFW/version, launch method, the last working
screen and any error code or screenshot. A fake SELF format check or emulator
decryption pass does not establish a physical-console boot pass.

## Restore

Quit the game and restore the twelve original files from your backup, or
restore the original game folder. Leave savedata and activation/license files
alone. Do not use the RPCS3-only modified PKG as a console installer.
