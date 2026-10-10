# Build 020 — attack artwork, keyword spacing and SR rewards

This local NPJB00689 CFW test build addresses the five supplied screenshots.

- Center Attack and Wide Attack now use English shared word cells in the
  map battle overview. The shared Attack word is also translated for its
  other consumers. Native sample rectangles, tint and animation remain intact.
- Crowe's ZONE link now has a space before “ran”. All 3,334 canonical story
  records were scanned for a link closing directly against an English word;
  this was the only match. One word moved to the next line to keep the existing
  870px dialogue limit. Speaker, source fingerprints, glossary references,
  keyword order and wrappers remain intact; no wording was changed.
- Maximum Break uses the Z3 artwork recipe requested by the user. Rengoku's
  source digest, 26-texture GTF block, big-endian nine-piece sprite records
  and anchors were independently checked. All nine English cells settle into
  contiguous quads; the duplicate Japanese sample is no longer reused.
  Combo Attack, Counter, Re-Attack, Support Attack and Support Defend use
  the corresponding Z3 lettering recipe on compatible Rengoku surfaces.
  The different small-badge atlas remains preserved.
- Both SR Point notification variants suppress the colored placeholder
  behind the full translated message. Bonus funds now use one caption and
  the preserved native amount field, with an 18px gap. The original fullwidth
  number, field pointer, color, height and vertical position remain intact;
  the caption does not repeat or replace the amount.

Ten focused regressions pass: reward variants and amount preservation,
keyword spacing and all dialogue bounds, actual attack UVs with drift rejection,
Maximum Break whole-letter sampling and unrelated-animation preservation,
and the build019 skill/bonus/objective regressions. Source and locale validation
passes. Atlas previews are diagnostic compositions, not gameplay screenshots.

Original extracted data, older local builds and the public v0.1.1 release are
preserved. This package requires the matching activated original game.
Gameplay, the corrected screenshot states and physical PS3 installation/boot
still require testing.

The complete folder, file overlay and archive readbacks pass. Offline RPCS3
decryption accepts the original stage, English stage and executable with
byte-identical output and exit code 0. The English stage SHA256 is
`cdfbccb0ee9515cbb5ce1abd748a3a125c010d40cee83e572a1cede9394e8bf0`;
the executable payload is unchanged from build019.

Local package: `SRW-Z3-R-NPJB00689-English-build020-CFW-test1.pkg`,
621,868,544 bytes; SHA256
`d60abf391ceca2f1b50a8dfe7c2d4aafaf3755ce7a42030e2cc0870b9a25ed93`.
All 77 packaged files, debug authentication and full cipher roundtrip pass.
The executable audit retains both native load segments, NPDRM metadata,
TLS and zero-filled BSS, with all 99 injected branches checked.

An independent isolated RPCS3 package installation produced all 77 expected
files with matching hashes. It then exited with the existing headless teardown
assertion (3221226505); this confirms extracted contents, not a clean program
shutdown, game boot or physical-console installation.
