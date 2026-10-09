# Screenshot layout corrections — build 005

The four user screenshots show a character-library description overflowing
the right edge, a Japanese operation heading, crowded terrain and stat fields,
and a split Ace Bonus heading. These fixes use NPJB00689 source assets. The
sibling Z3.1 project is a read-only rendering/tooling reference.

## Library

Rengoku's own FSSA sample records at `0x8f704` and `0x8f724` contain a 38-cell
ruler. Their horizontal text quad is 30 pixels. Description fields `DSCR` and
`DSC2` are now word-wrapped at 1,140 native pixels using the actual Rodin
advances, in both ZKAN and MTFL containers. Existing paragraph breaks and all
words are preserved. Blue's sample becomes six lines; its widest line is
1,100.625 pixels. Source English stays unchanged.

The three character-page nickname labels at `0x9cc84`, `0x9cea4`, `0x9cf24`
retain their positions and heights. Their horizontal quad changes from 31 to
27, leaving over ten pixels before the fixed name-value column. This keeps
the Nick and CV labels aligned. The clipped `: Expressions` hint at
`0x9ccc4` reads `: Face`.

## Operation heading

At VA `0x1dabd4`, Rengoku constructs an episode prefix using 第, fullwidth
decimal digits and 話. VA `0x1dafc8` concatenates the prefix, 『, the title and
』, in either UTF-8 or CP932. Therefore an exact lookup for the title alone
cannot translate the composed result.

The build adds complete-heading matches for the 15 cataloged chapter titles
at file offsets `0x95a538` through `0x95a650`, with episode counters 1–99 and
the final-episode prefix. Unknown titles do not match. Existing catalog
wording supplies the title: `第１話『翠の地球』` becomes
`Episode 1: Green Earth`. The counter is preserved, not inferred from the
position of the title in the table. This adds 1,500 exact mappings.

## Terrain and stats

Terrain uses Z3.1's natural-letter one-cell recipe: 11px capitals, baseline
20, 4x supersampling and 0.3px stem expansion. Air, Grd, Wtr, Spc and Und
were compared pixel for pixel against the sibling renderer. Each word
retains the native one-cell advance. `Only` uses the same small face.

The earlier fix handled the horizontal label string but physical insertion
had already expanded single-label and indexed-table strings. Both insertion
paths now map those labels to compact cells. The native movement composers'
UTF-8 tables at file offsets `0x888ec8` and `0x889128`, and three exclusive
movement strings at `0x888e98`, `0x888ea8`, `0x888eb8`, also use compact cells.
Every original byte sequence and replacement length is checked.

MEL/RNG no longer use miniature whole-word cells. Original UTF-8 stat fields
remain intact; the post-conversion draw lookup supplies three normal-sized
Rodin letters. Both labels fit within the original two-character width at
the 28px quad. Unit Info's narrow Focus labels (`0x9d5c4`, `0x9dd64`) use Foc.

## Pilot Info

The visible Ace Bonus heading is four **physical** FSSA records at `0x8a664`,
`0x8a684`, `0x8a6a4`, `0x8a6c4`: エ / ース / ボー / ナス. Translating and
relocating these independently destroys the adjacent source sequence needed
by the earlier runtime joiner. Build 005 sets the first record to the full
`Ace Bonus` and points the other three at empty strings. Other bonus labels
and the runtime joiner are preserved.

`精神コマンド` at `0x9d784` reads `Spirits`, with its original 28px width.
The italic kill-count suffix record at `0x8f044` uses a 31×31 glyph quad,
moves ten native pixels right and three pixels up. Screenshot color-mask
measurement found the original U at 32 displayed pixels high versus 43 for
the numeral 5; the size adjustment targets that difference. Final placement
still needs an in-game check.

## Verification and limits

Seven new regression tests cover the real FSSA records, unchanged unrelated
labels, library word preservation and line bounds, both stage-heading draw
paths, normal stat glyphs, guarded movement fields and exact reference
terrain masks. All 61 project tests pass. Canonical translations, source
assets and earlier builds are preserved. Build 004's link-background code is
unchanged.

Offline archive/readback and RPCS3 decryption checks are recorded in the
build folder. They do not validate final visual placement. Recheck the four
reported screens in RPCS3, including longer library pages, terrain ratings,
MEL/RNG, Ace Bonus and the kill-count suffix. Real PS3 hardware remains
untested.
