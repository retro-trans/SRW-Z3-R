# Search and ally-list layout — build 007

The supplied RPCS3 screenshots show four display problems: the selected
Spirit Commands tab exceeds its tab, the search-result caption and SP Cost
header overlap, Mind Resist's Effect description runs offscreen, and the
ally-list support columns and bottom Focus field overlap.

## Source-bound labels

`tools/rengoku_search_layout.py` relocates 26 physical FSSA display strings
in Rengoku's `AIDDATAPACK_R.CPK` member 0. Every source label is checked at
its own Rengoku record; all 28 non-pointer bytes of each record are retained.
In particular, the selected tab's byte value 160 is an encoded glow style,
not a font height to replace. No numbers, sort controls or column positions
move.

| Records | Correction |
|---|---|
| `0x96f24`, `0x97104` and three result-caption variants | Spirit Commands / Spirit becomes Spirits |
| `0x96f64`, `0x97144` and three result-caption variants | Special Ability becomes Abilities |
| `0x9d3e4`, `0x9d404` | Keep SP Cost once; blank the extra decorative SP suffix |
| Four Repair/Resupply pairs | Rpr. / Res. fit both the 72px and 80px column variants |
| `0x9f5c4..0x9f5e4`, `0xa3b24..0xa3b44` | Sup Atk / Sup Def fit the 128px support columns |
| `0x9ed84`, `0xa2684` | Foc leaves room before the fixed numeric value |

The real SP value-column label at `0x9d424` remains the original fullwidth
SP; it is not the redundant fragment. The new SP Cost width is 106.75px,
leaving about 27px before that column. The two narrow supply labels measure
58.625px and 60.375px. Support labels measure 106.75px and 109.375px. Bottom
Foc measures 45.3125px at its original 25px glyph size.

The sibling Z3.1 search-label and split-SP fixes were read as references.
Its executable addresses and FSSA offsets were not applied to Rengoku.

## Effect descriptions

The text originates in `RPW_DATA.CPK` member 0. Its SHA-256 is guarded:
`843f9d59af70515da1087c67bcffca7b570eb4a0eae2cb70e31bf06665f30872`.
Rengoku's own `sk-pri` array has 82 records of 13 words; columns 4 and 5
reference its long/short skill descriptions. Its `spirit` array has 44
records of five words; column 3 references the Effect description. The
zero records and final hidden Spirit entry are excluded.

This covers 162 pilot-skill fields and 42 Spirit fields: **204 bindings,
187 distinct source descriptions**. Every referenced source pointer must
be a real j-string start and match its canonical catalog occurrence.
The arrays, gameplay values and original RPW bytes are never changed.
The existing whole-string draw table supplies the wrapped English from
owned text storage, after the general translations have been installed.

The FSSA search-description ruler explicitly specifies two lines for
Spirits and up to three for skill/ability descriptions. The screenshot's
native text starts near x=141.5, with its right rule near x=1224 on the
1280px canvas. The visible overflowing prefix ending in “Negates Daunt”
measures 1142.75px with the Rodin 28px quad, matching the observed clipping.
The new 1000px width leaves more than 80px inside the right rule.
This is a screenshot-derived bound, not a new emulator rendering test.

Word wrapping preserves every word, punctuation mark, number and condition
from the canonical English. All fields fit their two-/three-line limits;
the maximum measured line is 999.25px. Both Mind Resist variants now read:

```text
Blocks stat-halving, action-stop, Focus-down and SP-down effects.
Negates Daunt when Focus is 100 or less. No effect for sub-pilots.
```

Their widths are 931.875px and 920.5px. No translation was abbreviated or
removed to make the prose fit. Names, other RPW fields, canonical English
and story dialogue remain unchanged. Descriptions in other, smaller panels
still require in-game review; this bound comes from the reported Search panel.

## Validation

Five new regressions cover selected/inactive tab widths, the real split
SP header, all narrow ally-list copies, unchanged style/value fields,
every effect's width/line count/word stream, and source guards. Both emitted
CP932 and converted-Unicode lookup paths are executed on both Mind Resist
variants; the returned owned strings contain the intended newline.

All **72 tests pass**. Evidence is in `work/build007_tests.log` and the
inspected `work/build007_dryrun.log`. Build 007 is complete: all 169 rebuilt
members and untouched archive members verify, and all three independent
RPCS3 offline decryption checks pass. Results are recorded in
`work/builds/rengoku_en_007/BUILD_REPORT.json` and `verification/RESULT.json`.
The final ELF table was independently walked to verify all 187 description
values, and the finished AID archive was reopened to check all 26 labels.
Only AID/EBOOT content differs from 006; the regenerated stage encryption
wraps byte-identical plaintext.

In-game checks still needed: selected/inactive Spirits and Abilities tabs,
the Scan results page, Mind Resist plus the longest descriptions
(Pressure, Tactical Standby and Direct Hit), both ally-list variants and
the bottom Focus number. Earlier narration, terrain, chapter artwork and
link-background fixes are retained. No installed game or save was changed.
