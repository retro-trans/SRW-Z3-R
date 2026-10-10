# Build 021 — condition/report corruption and name consistency

The supplied screenshots were taken with public v0.1.1 (build018). This local
NPJB00689 CFW test build includes the subsequent build019/020 corrections.

- SR Point conditions: all 72 operation-table occurrences, covering 37 unique
  Japanese sources, retain native Japanese during processing. Complete English
  is supplied from owned display storage. Episode 10 reads: “Defeat all enemies
  without letting a single enemy unit enter the town.” Its meaning was already
  correct; build021 adds a source-byte and complete-display regression for it.
- Tiamat's encyclopedia description now refers to the unit **Daimon**.
  The name pass scans every English catalog with a Japanese identity guard;
  ordinary demon references retain their meaning.
- **Asakim Dowin** follows the user's explicit spelling request. Six encyclopedia
  catalog records, one story record and the resolved glossary are consistent.
  The naming normalizer and active terminology decisions no longer restore
  the earlier Dowen spelling. Historical proofreading reports are retained.
- The upgrade-refund report retains its original GIFT tuple and numeric fields
  until display. The complete translation is provided through whole-message
  and individual-line hooks; each line fits the measured 1050px area. The scan
  of all original story files found one quoted GIFT notification, covering this
  entire producer category. No words are removed to fit the original buffer.
- Both Custom Bonus popup variants carry forward the build019 header join and
  removal of the duplicate colored placeholder. The full notification remains.
  All 17 selectable/custom bonus effects keep their measured wrapping.

Independent meaning review examined two 80-record slices: 160 in-slice records,
180 row views with adjacent context, and 170 distinct records. The 72-condition
category was also reviewed in full. No semantic changes were needed. The exact
native corruption producer remains an inference until gameplay tracing.

Thirteen focused regressions pass across builds019/020/021, including the
Episode 10 complete draw/conversion lookup, unchanged native GIFT tuple and
whole/line report lookups, both Custom Bonus variants, and the canonical name
scan. Source fingerprints and locale validation pass. The inspected build
preview includes 72 conditions, 17 bonus effects and the single GIFT report,
with no pending consumer-specific insertion.

Archive members, the complete folder, overlay and ZIP all pass readback checks.
Offline RPCS3 decryption accepts the original stage, translated stage and
executable with byte-identical results and exit code 0. The translated stage
SHA256 is `02f79b5ed3468437b12425f7d8187587f53bae442af63a1b69fe316e4584d959`;
the executable payload is
`d1e3cbb7871a6f84cee40ca495e505060c9f33fc46cad4c5669e2c8addc8f27b`.

Local package: `SRW-Z3-R-NPJB00689-English-build021-CFW-test1.pkg`,
621,868,464 bytes; SHA256
`f2c637f5a47d05157251c5851ff4e761e83549ee05e3d8c534bf43242fc52ae1`.
All 77 packaged files, debug authentication and complete cipher roundtrip pass.
The executable audit checks all 99 branches, both native load segments, TLS,
zero-filled BSS and preserved NPDRM identity/metadata.

Independent isolated RPCS3 installation extracted all 77 expected files with
matching hashes, then exited during the known headless teardown assertion
(3221226505). This verifies extracted contents, not a clean program exit,
game boot or physical-console installation.

Original extracted data, previous builds and the public v0.1.1 release remain
preserved. Physical PS3 boot and these corrected screenshot states require
testing on the matching activated game; its original license is still required.
