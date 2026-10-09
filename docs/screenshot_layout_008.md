# Team-list and System Settings overlap — build 008

The new screenshots identify another set of physical display records:
the Team-view support headings, the Move footer and the two System Settings
tabs. Build 007's Unit-view support headings are separate, wider records.

## Team support columns

The narrow heading pairs are Rengoku FSSA records `0x9f884/0x9f8a4`,
`0xa35e4/0xa3604` and `0xa4584/0xa45a4`. Their source text is the abbreviated
援攻 / 援防, rather than the full 援護攻撃 / 援護防御 fixed in build 007.
Two pairs are only 72px apart; the third is 112px apart.

Use the sibling Z3.1's compact S. Atk / S. Def treatment at a 21px glyph
quad, after identifying these records independently in Rengoku. Their
measured widths are 61.03125px and 63px. Center each label on its original
two-cell, 56px heading span. The narrowest pair then has about 10px between
labels; the last label ends near x=1219 on the 1280px canvas.

Only the six text pointers, horizontal positions and six font-size bytes
per heading change. Colors, vertical positions, rendering flags, sort
controls and level values remain intact. Wider Unit-view headings keep
their build-007 labels and sizes.

## Move footer

The English Move label is 63px wide at its original 24px size, but the
source leaves only 41px before the value bracket. Keep Move at x=361.5
and shift the three value components right by 32px:

| Source record | Content | Original x | New x |
|---|---|---:|---:|
| `0xa29a4` | Opening/closing brackets | 402.5 | 434.5 |
| `0xa29c4` | Terrain types | 477.5 | 509.5 |
| `0xa29e4` | Movement number and slash | 425.5 | 457.5 |

This leaves 10px after Move. The bracket's native 176px internal span and
25px closing glyph end at x=635.5, inside the 640px footer strip. The value,
slash, terrain cells and brackets retain their spacing and styles. Both
Move label templates at `0x9eea4` and `0xa2984` remain full size.

## System Settings tabs

All eight states at `0x96e24..0x96f04` now read Settings 1 / Settings 2.
Each label measures 155.96875px at the original 31px quad, within the
210px safe tab width. Only their text pointers change; native centering,
positions, colors, font sizes and selected/inactive styling are retained.

## Verification and remaining checks

`tools/rengoku_roster_settings_layout.py` implements 17 guarded display
edits. Canonical localization and original game assets are unchanged.
`tests/test_layout_build008.py` checks all eight tab states, all support
pairs, footer clearances/internal spacing, unrelated-byte preservation,
and rejection of changed source styles. All 76 tests pass, including these
four new regressions.

The dry run was inspected before packaging. All 169 rebuilt members and
untouched archive members verify. Three independent RPCS3 offline decrypt
checks pass. The finished AID archive contains all 17 new edits and all 26
build-007 label fixes; every unrelated byte of its prior FSSA is preserved.
The executable is byte-identical to 007, preserving Effect wrapping and
runtime fixes. The regenerated stage encryption has unchanged plaintext.

Evidence is recorded under `work/build008_tests.log`,
`work/build008_write.log` and `work/builds/rengoku_en_008/`, including
`verification/RESULT.json`. Final in-game appearance still requires
checking both settings tabs and Team-view support/footer layouts. Previous
font, description wrapping, terrain, narration, chapter and link fixes remain.
