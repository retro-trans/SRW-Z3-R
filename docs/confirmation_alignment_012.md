# Confirmation alignment regression — build 012

The user's End Phase screenshot shows the selected orange **No** left of
the gray **No** underneath it. This supersedes build 009's offline claim
that its width calculation aligned the two layers.

## Cause

Builds 009–011 treated the six confirmation rows' 25px character pitch as
their glyph quad width. Rengoku's own font preset 1 instead uses **28px
quads and 25px pitch**. The blank proportional spacer therefore placed the
slash 84px after the line origin and No at 134px. The active No was at the
correct native column, 125px, giving the observed nine-pixel difference.

Source evidence, independently checked against NPJB00689:

- AID member 4 has 13 font presets, count at `0x484`, table at `0x488`.
  Preset 1 at `0x498` contains `(28,28,26,28,28,28,26,28)`.
- FSSA record byte 22 selects preset 1 in every affected row. Bytes 16–21
  are character pitches, not the preset's glyph dimensions.
- Loader `0x61410` passes the member to `0x5e058`; its table pointer lands
  at the layout object's `+0x518`. The record renderer reads this pointer
  at `0x5f634` and selects the preset at `0x5f63c`.
- The native glyph style path `0x144c8..0x145e0` chooses quad/pitch. The
  native advance loop at `0x147d8..0x147e8` uses stack `+0x84` for pen x,
  `+0x94` for native pitch and `+0x9c` for glyph width. The draw routine
  keeps the line origin in `f31`, assigned at `0x14180`.

## Correction

The existing invisible confirmation cell is now a tab to
`line_origin + 3 * live_pitch`. Native fullwidth slash and space then put
No at column five. The existing active rows stay left-aligned at the
matching columns, preserving the native cursor spans.

This uses the same live-pitch tab approach as Z3.1, with Rengoku's own
guarded addresses and allocated glyph cell. No sibling executable offsets
are transplanted. The blank mask and all visible glyphs remain unchanged.
The ordinary glyph advance path remains unchanged; only this reserved
cell takes the new branch. No story, menu wording or choice logic changes.

Affected background / active pairs:

| Background | Active | Selected word |
|---|---|---|
| `0x8bd24` | `0x8bd44` | Yes |
| `0x98f84` | `0x98fa4` | Yes |
| `0x99364` | `0x99384` | Yes |
| `0x993a4` | `0x993c4` | No |
| `0x993e4` | `0x99404` | Yes |
| `0x99424` | `0x99444` | No |

## Validation

`tests/test_confirmation_build012.py` executes the game's native style
selection and the emitted PowerPC advance code, including the native
pen add/store. It first reproduces the nine-pixel error using the exact
old adapter and width 41. The corrected build matches both letters of
No and all three letters of Yes against their background counterparts
for every pair. It also checks 144 combinations of origin, pitch and
quad size, register preservation, keyword advance accumulation, and
the unchanged advance of every other mapped glyph.

The old build-009 test now checks only record metadata; it no longer
mistakes an arithmetic width sum for a renderer alignment test.

Build 012 is complete under `work/builds/rengoku_en_012/`. All 100 tests,
172 member readbacks and three independent offline RPCS3 decrypt checks
pass. The packaged ELF's 132-byte advance adapter at `0x8fb770` equals
the tested output, with confirmation cell `0x83f0`. ELF SHA-256:
`130fac1da279ee28f65825f62541049caccd0b1af0619b4eb3175e3c63221478`.

The RPCS3 folder contains 78 files; the matching CFW/HEN overlay contains
12 files. ZIP size is 75,826,194 bytes; SHA-256:
`f1b0d960b2394c2dc67743313ebdffb0b695ec539635c03e0c6733e0c5c3592b`.
Only EBOOT and regenerated stage encryption differ from 011. The stage
plaintext and all 76 other game files match; glyph mappings, lookup text,
translations and artwork remain unchanged. Original sources, previous
builds, installed games and saves were preserved.

These are offline instruction-level checks. They do not establish visual
acceptance in RPCS3 or compatibility on real PS3 hardware. Recheck End
Phase with both Yes and No selected, plus save/quit confirmation variants.
