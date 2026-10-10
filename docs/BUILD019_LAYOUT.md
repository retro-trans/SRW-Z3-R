# Build 019 — skill, bonus, dialogue and objective corrections

The five supplied screenshots were checked against NPJB00689's original
tables, canonical English and Rodin glyph advances. This is a local CFW test
build; the corrected screens have not yet been verified in gameplay.

- Skill Learn and the wider Effect panel share description hooks. All 162
  pilot-skill description bindings now use the narrower 760px / 32px-quad
  limit, with at most three lines. The 42 Spirit descriptions retain their
  separate 1000px / 28px-quad, two-line limit. Ten skill descriptions were
  source-reviewed and shortened without removing mechanics or conditions.
- Generated level labels now cover the level-bearing skill category,
  including Ignore Size L1, Commander, Newtype and bonus levels. Existing
  glossary spellings are retained.
- Both Custom Bonus popup variants now use a complete header and remove
  the static placeholder behind the live notification. Full Upgrade Bonus
  fits its header. All 17 selectable/custom bonus effect entries were measured;
  weapon and song range effects retain both MAP and range-1 exclusions.
- All 3,334 story records were scanned; spoken records were checked against
  three body lines and an 870px width at 32px quads. The 162 affected dialogue
  records were corrected: 158 by lossless reflow and four through source review.
  Speakers, fingerprints, glossary references, keyword order, substitutions
  and speech/monologue wrappers remain intact.
- The Episode 7 SR Point text is complete in the canonical locale. Its meaning
  is to defeat every enemy by the time the victory condition is fulfilled.
  The displayed `c+` is a runtime defect. All 72 operation-table entries now
  retain original Japanese inside native processing buffers and receive full
  English from owned draw-time storage. This avoids placing expanded encoded
  English into those native buffers. The exact live producer of the corruption
  has not been traced; the changed path requires a screen retest.

Six focused regressions pass, including original operation-table byte
preservation, complete SR Point lookup in both emulated draw paths, generated
skill levels, popup variants and all dialogue widths. Five existing Effect
regressions and three package-format tests pass. New build archive readbacks,
source identities and offline stage/executable acceptance pass. None of these
checks constitutes an in-game or physical-console result.

The layout audit used 42 consecutive 80-record story slices, shortened only
at member ends: 2,509 records within slices, 2,683 views with adjacent context,
2,573 distinct records. Meaning reviews independently examined 480 records
in six skill/bonus slices (525 distinct with context), 160 records in the
original story/objective slices (173 with context), and 240 records in the
three additional story slices (260 with context). Layout-only reflows do not
claim a fresh meaning review of every dialogue line.

Remaining editorial findings outside these fixes: STG00028 row 79 contains
uncertain wordplay; five Power Part descriptions around RPW 1154–1159 say
"all allied units" where the source specifies units in an allied team. These
remain recorded for a separate source review. Proposed Dimensional Power
terminology for `次元力` retains its existing review warning.

Retest the five supplied screens, both bonus popup variants, other long skill
descriptions, numbered victory/defeat conditions and save/load in a separate
slot. Keep the matching original activation/license and an original game
backup when installing the CFW test PKG. Public release 0.1.1 is unchanged.

Local output: `work/builds/rengoku_en_019_cfw_pkg_test1/`
`SRW-Z3-R-NPJB00689-English-build019-CFW-test1.pkg`, 618,486,032 bytes;
SHA-256 `45df9ac98129fa34ccce31e1e6f7bb611057b2020edc3f62ffeadf589fdef033`.
Full cipher round trip, authentication and 77 packaged member hashes pass.
An independent native RPCS3 installer produces all 77 expected files exactly;
its known headless teardown assertion 3221226505 remains. No physical PS3
installation, boot or corrected-screen gameplay test has been performed.
