# Build 022 — upgrade selector, keyword gaps, ending dialogue and credits

This local NPJB00689 CFW test build addresses the five additional public
v0.1.1/build018 screenshots and carries forward builds019–021.

- Full Upgrade Bonus selector: fit all four terrain captions, Movement,
  Part Slots and Barrier/armor EN cost beside the native rank/value fields.
  The complete barrier-cost meaning comes from that caption plus the existing
  live “Halved” value. Measured 28px lettering leaves at least 21px before that
  value. Only caption pointers change; rows, coordinates, colors, glyph sizes,
  rank values, slot icons and selection behavior remain native. The joined,
  fitted Full Upgrade Bonus header and wrapped effects from build019 remain.
- Episode 13 SR condition: the complete English is “Have any one allied unit
  defeat at least 7 enemies.” No source qualification is missing. All 72 native
  operation strings continue to be retained until owned English display lookup;
  build022 adds a regression for this particular condition and its source table.
- Aim spacing: checked all 3,334 story records for an English letter/digit
  touching an opening keyword wrapper. Corrected both matches, STG00092 rows
  68 and 75. Existing source IDs, link order and keyword references remain.
- Ending dialogue: corrected STG00107 row45 so travel between the Earths becomes
  possible, rather than the planets themselves traveling. Its full meaning fits
  three measured lines; adjacent dialogue confirms the subject. A corpus scan
  found no other record with the same travel wording.
- Credits: measured all 333 nonempty native text rows. English columns use
  measured spaces, with the second column near x704 instead of inheriting long
  Japanese padding after names of different widths. All rows fit x64–1184 at
  a 32px glyph width, without dropping or abbreviating names. Native Japanese
  fields are retained until owned display lookup. The 439-record structure,
  all 30-byte commands, blank rows, scroll cues and 42px row pitch are unchanged;
  only the native header's glyph-width and advance bytes change from 36 to 32.

Independent meaning review: four 80-record slices, 320 in-slice records and
350 distinct records including 30 adjacent-context records. One subject fix;
no unresolved meaning choice for these targets. User spellings Daimon and
Asakim Dowin remain unchanged. Exact corruption producer and corrected screen
appearance still need gameplay verification.

Seventeen focused regressions and canonical/source validation pass. The build
preview has no pending consumer-specific insertion, and includes all 333 credit
rows, the selector captions, 72 conditions and the previous bonus/report fixes.
Both draw paths return complete owned English for the reported credits names.

All archive members, the complete game folder, overlay and ZIP pass readback
checks. Three offline RPCS3 checks accept the original stage, translated stage
and executable with byte-identical results and exit code 0. Stage SHA256:
`e6f671ebe28a8251270fcc8591bf023079fcf0532333dcbd2dff3963f56490b0`;
executable payload:
`92d6aea14d2483f1fae20a9572e239ccecdb88c891e667f21896fbe505c71d7a`.

Local package: `SRW-Z3-R-NPJB00689-English-build022-CFW-test1.pkg`,
621,868,688 bytes; SHA256
`2bcc308add953d165a2b00cb072bc317a19445e2e19786f64cb59ca39f988489`.
All 77 packaged files, debug authentication and full cipher roundtrip pass.
The executable audit checks all 99 injected branches, both native load segments,
TLS, zero-filled BSS and preserved NPDRM identity/metadata.

Independent isolated RPCS3 installation extracted all 77 expected files with
matching hashes. The known headless teardown assertion then returned exit code
3221226505; this confirms contents, not a clean shutdown, game boot or a physical
PS3 installation. Corrected screens and hardware boot remain pending testing.

Public v0.1.1 and older local builds remain preserved. This package requires the
activated matching original game and its original license.
