# Build024 — automatic version and Retro Trans credit

User request, 2026-10-10: use the sibling's lower-right title credit/version
treatment and update it whenever a build is created.

The press-any-button screen now receives two right-aligned lines:
`v0.1.3` and `github.com/retro-trans`. Placement and font recipe match the
sibling: a 340x56px rectangle at (912,640), 28px from the right edge and 24px
from the bottom; 18px text, 4x supersampling and a dark outline.

The insertion is independently bound to NPJB00689 EFF member 133, GTF
0xecfe0, texture 0, a linear ARGB32 1280x720 background. Source member SHA256:
`e13739e4e1b893bb2dcd1eaddf3c15921b6d0d7efed6e9173c2d8c335460f95a`.
Original background SHA256:
`9e0f3820a99d54df08ddba114f4c341eba1868c2793c745da6d7911a11b12b4c`.
No sibling animation/executable address or background is transplanted.
Only footer pixels change after the existing title/Library patches; all
animation commands, English title/Library sprites, native Z samples and the
other eight textures remain intact. The preview is an extracted asset,
not a running-game screenshot.

`tools/build_game.py` automatically chooses the next semantic version from
`build_version.json`. `--version` may request a newer version. A complete
build records matching version/footer fields in BUILD_REPORT.json and stamps
build_manifest.json after folder/archive/ZIP readbacks finish. Dry runs and
failed builds leave the counter unchanged. A concurrent counter change,
unfinished insertion or mismatched footer blocks the success stamp.

`verify_game_build.py` independently checks the packed member. CFW and RPCS3
packaging repeat this check and include the matching semantic version in
their validation metadata. Release packaging rejects a version mismatch.
MEMORY.md, AGENTS.md and BASE_RULES.md preserve the rule for future work.

Six focused footer/counter regressions, five existing title-art checks and
three runtime-PKG checks pass. Both original resources and previous builds
are read-only. Fresh build024/v0.1.3 is complete and passes all archive/folder/
overlay/ZIP readbacks plus the independent packed-footer check. The successful
counter now reads 0.1.3, and the next automatic version is 0.1.4. The executable
and decrypted story archive are byte-identical to build023; only title pixels
and regenerated encrypted SDAT wrapping differ. All three offline RPCS3
decryption checks exit 0 and match their expected plaintext/ELF bytes.

The local CFW package is
`work/builds/rengoku_en_024_cfw_pkg_test1/SRW-Z3-R-NPJB00689-English-build024-CFW-test1.pkg`:
621,868,688 bytes, SHA256
`5823621a5403d61f646e27eb78a20c0e30ddfbc59b92cdf88d9818a7ea3e344f`.
Its metadata records version/footer 0.1.3 and the Retro Trans credit.
Full package encryption/decryption roundtrip, authentication and all 77
member hashes pass. An isolated native installation matches all 77 member
hashes (`work/rpcs3_cfw_pkg024_test1/INSTALL-VALIDATION.json`), with the known
teardown assertion 3221226505 retained separately. Corrected title-screen gameplay and physical PS3 boot
remain untested. The package stays local; public v0.1.2 is unchanged.
