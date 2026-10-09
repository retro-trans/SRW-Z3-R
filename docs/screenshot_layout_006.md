# Narration, chapter cards and vertical terrain — build 006

The four supplied screenshots show build 005: Foc, full-size MEL/RNG and
compact movement types are present, but the opening text exceeds the right
edge, the chapter animation is Japanese, and the vertical terrain field
still overlaps its right-hand ratings. This pass addresses those three paths.

## Timed narration

`AIDDATAPACK_R.CPK` members 13/14 contain 25 opening and seven ending rows.
They have a 20-byte header, respectively 71/49 records, and strides 78/84.
The record stride is header byte 2 plus 30. Empty records also contain
animation, delay and scene commands: they must not be cleared or repurposed.

Independently located Rengoku renderer sites:

- VA `0x58e28` loads the resource pointer from object `+0x3d4`.
- `0x58e2c..0x58e84` reads header bytes 4, 5, 6, 7 and passes them to
  `0x13884`, which stores width, height, advance and line pitch in the active
  font state at `+0x54/+0x58/+0x5c/+0x60`.
- `0x58f4c` reads unsigned header byte 9 for the left coordinate. The native
  row consumer at `0x58ad8` passes it as the draw x at `0x58c48`.

The old layout was x=224, glyph 38x43, advance 38, line pitch 60. The new
layout is x=96, glyph 32x36, advance 32, with a 1,088px safe width on the
1,280px canvas. The 60px pitch, scroll speed, record count, empty rows and
every byte after the header are identical to the originals. English remains
in owned draw-hook storage; no longer text is copied into native row slots.

Two adjacent pairs in the opening are reflowed across their existing rows:
the parallel-world sentence and the Geminaids/Prison of Time sentence. Every
word and punctuation mark remains in sequence within its original paragraph.
The remaining rows retain their existing English line breaks. All 32 rows
are measured with the actual Rodin glyph advances, including spaces. No
inserted row contains a newline. Source header and row fingerprints are
checked before building. The canonical translation catalogs are unchanged.

## Vertical terrain

The prior helper recognized individual terrain characters and horizontal
strings, but missed `空\n陸\n海\n宇`. This is one four-line string, with 22
catalog occurrences. Its expanded English was physically inserted into
FSSA, bypassing the short-label lookup and overlapping the right rating.

`text_for_field` now preserves newline separators while converting each
terrain character to one compact cell. The complete multiline draw hook is
also covered. The display is Air / Grd / Wtr / Spc using the same compact
glyph masks already compared with Z3.1. Native quad size, line pitch and
rating coordinates are preserved. A regression walks the actual source
FSSA records, checks their relocated bytes, and compares all 28 non-pointer
metadata bytes. It also executes the generated draw hook on the whole field.

## Chapter artwork

All 15 existing canonical title translations are now rendered into
`TPACKPS3.CPK` members 4–18. Each original GTF is a linear ARGB 1536x256
texture with normal and glow rows. Titles are centered, fit inside the same
texture bounds, and retain a separate glow copy. Source hashes bind each
image to `source/artwork.json` and `localization/locales/en/artwork.json`.

The title renderer uses the local PS3 Seurat Latin Regular face, matching
Z3.1's chapter-art recipe. Dialogue and interface letters remain Rodin Bold.
This is deterministic font rendering into the game's native textures.

A scan of Rengoku's 136 effect members identified the numbered and final
chapter animations in `EFFPS3.CPK` members 100, 101 and 102. These are this
game's members, not the sibling's 87–91:

| Member | Embedded GTF offset | Purpose |
|---|---|---|
| 100 | `0xdf450` | One-digit episode header |
| 101 | `0x101c70` | Two-digit episode header |
| 102 | `0xc5ef0` | Final Episode and embedded final title |

The numbered resources use mode words `0x0101/0x0201`, unlike the sibling's
`0x0100/0x0200`. Ignoring that difference would silently miss every quad.
The new builder guards complete Rengoku resource hashes and verifies these
animation counts: 1,691 prefix quads; 1,674 or 3,348 digit quads; 1,650 suffix
quads. It expands the prefix for Episode, shifts digit x by 128 units, and
hides the old 話 suffix using its vertex colors. Native digit pixels, timing,
mode words, unrelated quads, backgrounds and logos remain intact.

All three atlases have their Final Episode region translated. Member 102
also replaces the normal/glow embedded `死闘の果てに` title with its canonical
English. Its animation geometry is unchanged. Numbered resources retain
the native dynamic-title mechanism and receive an English fallback texture.

The 15 titles plus three animation resources are source-bound and checked
individually. Original/English atlases and the title contact sheet were
inspected under `work/chapter006_final_preview/`. These are asset proofs,
not emulator screenshots. Other 167 cataloged artwork/manual blocks still
await raster insertion; this pass covers chapter cards, not all game artwork.

## Validation and remaining check

Six new regressions bring the suite to 67 passing tests. They check real
FSSA metadata, all narration rows/cues/word streams, source guards, all 15
texture pairs, every numbered animation quad, final-card rectangles, and
preservation of unrelated artwork. Build logs are under `work/build006_*`.

Build 006 is created in a new directory. Build 005 and all originals are
preserved. The final report and `verification/RESULT.json` record archive
readbacks, identical overlay/ZIP payloads and offline RPCS3 format checks.

Runtime visual QA remains necessary: replay both photographed narration
pages, inspect the four terrain labels beside both rating columns, and
check episode 1, a two-digit chapter and the finale. Also replay the ending
narration. Offline validation does not establish final appearance, animation
blending, gameplay stability or real PS3 loading.
