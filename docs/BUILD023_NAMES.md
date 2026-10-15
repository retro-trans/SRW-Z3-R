# Build 023 — requested name spellings

The user requested **Crowe Bluest** and **Elgan Roddick** on 2026-10-10.
These are explicit project spelling overrides, including the surname aliases
**Bluest** and **Roddick**. Earlier wiki/inherited alternatives remain historical
provenance, not the active translation.

- Scanned all 12,905 active locale records. Updated five direct non-dialogue
  targets: Crowe's full name, surname and credits, and two ZE XIS descriptions.
- Updated four effective glossary forms, the active character profile,
  terminology configuration and both proofreading do-not-touch collections.
  Normalization retains the requested spellings on subsequent passes.
- The glossary change reaches 13 story records and three stored battle
  references without changing their Japanese references or keyword order.
  The Blue screenshot is `STGZ3REN_00004:00011`.
- All affected story lines fit the measured 870px width at the actual 32px
  font size; the largest affected line is 848px. The Elgan screenshot's three
  lines measure 696px, 761px and 740px. Name widths are 208px for Crowe Bluest
  and 226px for Elgan Roddick at 32px.
- Story, battle and non-dialogue source-binding validation pass. No old
  Broost/Rhodic spelling remains in resolved runtime text. Repeating the
  name correction previews zero changes.
- Generated story, battle and non-dialogue reading copies were refreshed.
  Source IDs, source fingerprints, substitution markers and wrappers remain
  intact. The inherited glossary and sibling project remain read-only.

## Local build and package verification

Fresh output: `work/builds/rengoku_en_023`. All archive, folder, PS3 overlay
and ZIP readbacks pass, with zero pending consumer-specific insertions.
Offline RPCS3 checks accept the original stage, translated stage and
executable and produce the expected bytes. The initial original-stage check
timed out before producing output; its successful retry and first-attempt
report are both retained under the build's `verification` directory.

The complete local CFW test package is
`work/builds/rengoku_en_023_cfw_pkg_test1/SRW-Z3-R-NPJB00689-English-build023-CFW-test1.pkg`.
It contains all 77 game files and is 621,868,688 bytes, SHA256
`1418fe0e1bd9add142bcfbbbfefca8e08f0d66c0d8a6f0d0e9f74aff9b0e3149`.
Authentication, full encryption/decryption roundtrip, all member hashes and
99 direct executable hook branches pass. Original inputs remain unchanged.
An isolated native RPCS3 installation also matches all 77 package member
hashes (`work/rpcs3_cfw_pkg023_test1/INSTALL-VALIDATION.json`). Its known
teardown assertion exit 3221226505 remains; no gameplay was started.

The package remains local. Published v0.1.2 assets are unchanged. Corrected
gameplay screens and physical PS3 boot still require testing.
