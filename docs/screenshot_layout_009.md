# Command selection, map panel and confirmation layers — build 009

The confirmation alignment below was disproved by the user's subsequent
RPCS3 screenshot. [Build 012](confirmation_alignment_012.md) corrects the
quad/pitch assumption and reproduces the old error in an instruction-level
test. The Ally/Enemy and map-panel changes remain intact.

Target: PS3 Rengoku-hen NPJB00689. The user reported that both Ally/Enemy
choices appeared bright, then supplied an overflowing map-hover panel and
a selected No label displaced from the inactive label underneath it.

## Ally/Enemy states

`tools/rengoku_command_layout.py` edits only four source-guarded records in
Rengoku's AID member 0:

| State | Record | Text | Tint |
|---|---|---|---|
| Ally selected | `0x978e4` | Ally / | Original `a0a0ffff` |
| Ally selected | `0x97904` | Enemy | Dim `606060ff` |
| Enemy selected | `0x97924` | Ally | Dim `3c3c60ff` |
| Enemy selected | `0x97944` | / Enemy | Original `ffffffff` |

Both pieces use 28px glyphs, the same baseline and a 10px gap. The complete
row stays centered at native x=639.5 and fits within 200px. This follows
the geometry in the read-only Z3.1 `tools/command_layout.py:split_labels`;
all records, glyph widths and centering here belong to Rengoku.

The inactive RGB multiplier is 96/255. Alpha, faction palette selection,
navigation and remaining state flags are unchanged. This explicitly adds
contrast; it is not a claim that Z3.1 used this exact RGB multiplier.
Rengoku's own renderer was disassembled independently: `0x5f770` loads the
record's RGBA tint, `0x13958` stores it at font-state +0xa4, and `0x1423c`
passes it to `0x139dc` for multiplication by the native palette. No code
patch is needed for dimming.

## Map-hover panel

`tools/rengoku_map_panel_layout.py` updates the scoped source records:

- Five Spirit-status strips (`0xa7044` through `0xa70c4`) retain exactly
  17 two-byte cells, their original pitch, positions, colors and alpha.
  Whole names become Va/So/Fs/Al/Wa/Gu/Fo/St/Ac/Ze/Me/Sn/As/Fu/Lu/Ga/Di,
  plus An in the enemy variant; its slash remains intact. Each native
  status index therefore addresses the same cell in both the background
  and active overlay. Complete source-strip draw hooks use the same cells.
- Eighteen new cells use Z3.1's Spirit-label recipe: 16px cap, baseline 23,
  2px gap between cropped letter ink and at most 28px total ink. Their
  advance remains one native cell. Existing letters and terrain cells
  keep their allocations and masks.
- Five support variants use Atk./Def. at 18px, within 50px. Original
  selected/inactive alpha and the two-line variant's line spacing stay.
- Three movement labels use MV at 22px within 36px. Eight small Focus
  fields use Foc at their original sizes. The recovery labels use Rec:
  on both lines within 54px; HP/EN and percentage values stay in place.

The sibling's map-popup and compact-cell tools were read as references;
no sibling binary offsets were copied.

## Confirmation labels

Six background/selected record pairs are covered, including both centered
and left-aligned originals. The background row is Yes + an invisible
measured spacer + the native slash/space + No. The spacer fills exactly
three native 25px cells before the slash, placing No at column 125px.

Selected Yes/No are left-aligned at background x + 0/125, so the same
glyphs are drawn at the same positions in both layers. Original cursor
spans, colors, line spacing and value templates remain unchanged. This
uses a blank glyph and data edits, without a new runtime hook. The native
left-aligned draw entry `0x14ae4` directly branches to `0x14158`.

## Validation

All 85 tests pass, including nine focused checks for both selection tints,
complete-row bounds, all Spirit slot indices, map label bounds and style
preservation, six exact confirmation alignments, native tint-path
instructions and strict edit scopes. All 18 compact Spirit masks match
Z3.1's reference rasterizer pixel for pixel. The final 122-cell font proof
was inspected.

The dry run was inspected before packaging. All 169 rebuilt members and
untouched archive members verify. The finished AID contains all 38 scoped
record edits and expected strings; every unrelated byte from build 008
and every other AID member is preserved. Both packed font pages match the
current renderer, with differences limited to new Spirit cells. Existing
font mappings, chapter artwork, other TPACK members and every PowerPC
adapter are unchanged. Both compact-strip lookup strings are present in
the new executable; its lookup retains 11,654 pairs.

Three independent RPCS3 offline decrypt checks pass. Stage plaintext is
unchanged; the new ELF payload has SHA-256
`d0c64ae7e6f02d215094de330694edf5dbb5e5e7b716584f79445c1a6db582f9`.
Build 009's complete RPCS3 folder has 78 files including the manifest,
602,848,649 bytes. Its matching 12-file overlay ZIP is 76,298,090 bytes,
SHA-256 `78f259c63bc63a99efd42e9838168d0ac97bddcc40b3531a7e141317eee5768b`.
Evidence: `work/build009_tests.log`, `work/build009_dryrun.log`,
`work/build009_write.log`, and `work/builds/rengoku_en_009/verification/RESULT.json`.
Original assets and canonical translations are unchanged; prior builds
remain available. No installation, game boot or save changes were made.

In-game appearance must still be checked on both Ally/Enemy selections,
the hovered-unit panel and Yes/No confirmations. Offline checks do not
substitute for RPCS3 gameplay or real-console verification.
