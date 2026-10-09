# English test build 018 — 2026-09-26

Target: PS3 Rengoku-hen, NPJB00689. The build is packaged for RPCS3 and PS3
with CFW/HEN. User screenshots confirm earlier builds reached gameplay and
Back Log. Build 018's final layouts and real hardware compatibility are not
yet verified in game.
Stock PS3 firmware is not a target of this fake SELF build.

## Outputs

All outputs are local and ignored under `work/builds/rengoku_en_018/`.

| Output | Purpose |
|---|---|
| `RPCS3/NPJB00689/` | 77 game files plus extraction manifest, 618,373,897 bytes total |
| `PS3/NPJB00689/` | 12 changed files to overlay on the matching original installation |
| `SRW_Z3_Rengoku_English_018_PS3_RPCS3_overlay.zip` | Same overlay, with instructions; 75,776,024 bytes |
| `README.md` | Setup instructions and test-build limitations |
| `BUILD_REPORT.json` | Source hashes, per-asset edits, font mapping and coverage |
| `SUBTITLE_LAYOUT.json` | Changed subtitle rows, widths and 45 pending entries |
| `INTERMISSION_REVIEW.json` | Nine 80-record slices and adjacent context for the new labels |
| `SHA256SUMS.txt` | Changed game file and ZIP hashes |
| `font_preview.png` | Inspected font proof; not an in-game screenshot |
| `intermission_heading_preview.png` | English heading word cell; not an in-game screenshot |
| `title_preview_large.png`, `title_preview_menu.png` | Inspected native-sprite compositions; not gameplay captures |
| `library_buttons_preview.png`, `chart_preview.png`, `chart_longest_title_preview.png` | Menu and chart compositions with real glyph masks; not gameplay captures |
| `verification/RESULT.json` | Independent RPCS3 offline decryption results |

ZIP SHA-256:
`4e41693ce38e0cef445275af637b0d33b13cdb117a7daee2b12405f438bb3bd2`.

Builds 001–017 are preserved. Build 018 retains build 003's replacement of Arial Regular with the
same Rodin Latin Bold font and letter recipe as the sibling Z3.1 project:
22px cap height, baseline 26, 4x supersampling and 0.5px stem thickening.
All 95 printable ASCII masks and advances were compared against the sibling
renderer and matched exactly. Segoe UI Symbol supplies missing symbols.
The finished 122-cell font proof was inspected, including 18 compact Spirit
labels whose masks match the Z3.1 reference exactly and one blank alignment cell.

## New in 018

The Intermission heading is English. Team Setup, D-Trader, SR Points and
Z Chips are joined captions; Parts clears the NEW badge. Repeated deployment
suffixes and score Units labels are removed. The first score shares a suffix
with Pilot Info, which therefore also displays a bare kill count.

Pilot List and training use MEL/DEF at the existing font size. Footer labels
move left to clear their live values. Training tabs read Raise Stats and
Learn Skills in all four states; PP Held, PP Cost and PP Left replace the
overlapping two-column fragments. See [source binding and bounds](intermission_018.md).

All 118 tests, 173 archive-member readbacks and three independent offline
RPCS3 decrypt checks pass. Review covers 720 in-slice records and 780 unique
records with adjacent context, with 62 label overrides and 20 footer shifts.
Packed comparison changes only the listed AID member 0 fields and member 1
word cell; other archive plaintext, executable, font and canonical inputs
match 017. `work/builds/rengoku_en_018/verification/RESULT.json` records
all_passed=true. In-game visual acceptance remains pending.

## Retained from 017

The Combo map popup now scales with map zoom once. At full animation size,
its quad occupies one 64-unit grid tile, preserving the original yellow
lettering, +1/+2/+3/+4/MAX frames, center, color and animation timing. At
zoom 0.5 the text is 60% larger in each dimension. Other popup states keep
their native sizing. See [source evidence and tests](combo_popup_017.md).

All 114 tests and 172 archive-member readbacks pass. Comparison against
016 allows only one four-byte instruction and an 84-byte adapter in the
executable. All archive plaintext, font, artwork, SRVC, AID and canonical
inputs match. Offline RPCS3 acceptance is recorded in
`work/builds/rengoku_en_017/verification/RESULT.json`; in-game appearance
and real PS3 execution remain unverified.

## Retained from 016

Both matching battle Fast Forward prompts read Fast, clearing the Cancel
icon while retaining the original font sizes and button positions. Each
fits within its original four-cell caption space with a margin. See
[source bindings and dimensions](battle_controls_016.md).

All 110 tests, 172 member readbacks and three independent offline RPCS3
decrypt checks pass. Packed AID member 0 changes only two pointers and
22 appended bytes; the other 15 members match 015. Only AID and regenerated
stage encryption differ among the game files. Executable, SRVC, font,
artwork, canonical inputs and stage plaintext remain unchanged. In-game
visual acceptance and real PS3 execution remain pending.

## Retained from 015

Battle results label the score column Kills and omit the compact counter's
Units suffix, clearing the Level column. All live values, font sizes,
positions and colors stay unchanged. Build 018 additionally removes the
shared Pilot Info/Intermission suffix. See [source bindings and scope](results_score_015.md).

All 110 tests, 172 member readbacks and three independent offline RPCS3
decrypt checks pass. The packed AID differs from 014 only in member 0's
three text pointers and 13 appended bytes; all other 15 members match.
Only AID and regenerated stage encryption differ among the 78 game files.
Executable, SRVC, font, artwork, stage plaintext and canonical catalogs
match 014. In-game visual acceptance and real PS3 execution remain pending.

## Retained from 014

Blue's battle-animation quote breaks after “Mass-produced or not,” so the
two generated rows fit before the right status icons. The display-only SRVC
transform preserves words, wrappers, font and canonical catalogs. It wraps
464 unique messages / 609 stored occurrences within 730px and two rows;
45 longer entries remain unchanged pending separate storage/layout work.
See [native conversion evidence, bounds and limitations](battle_subtitles_014.md).

All 108 tests, 172 member readbacks and three independent offline RPCS3
decrypt checks pass. Tests execute Rengoku's native newline converter,
check the intermediate buffer and read back all 6,356 voice cues. Only
SRVC and regenerated stage encryption differ from 013. Executable, stage
plaintext, AID, artwork, font mapping and canonical inputs are unchanged.
No installed game or save changes. In-game visual acceptance is pending.

## Retained from 013

Battle-preview captions use Rnd., EN, Foc and Atk. to clear the native
colons, values and target arrow. Matching support, defense, second-attack
and Song EN variants are compacted in the same 15-record layer. Font size,
positions, live values, colors and animations are preserved. See
[source evidence, caption decisions and checks](battle_preview_013.md).

All 104 tests, 172 member readbacks and three independent offline RPCS3
decryption checks pass. Packed comparison against 012 changes only AID
member 0's 15 string pointers and appended labels. All 15 other AID members
match. All game files match except AID and regenerated stage encryption;
the stage plaintext is unchanged. Executable and all preceding corrections,
including No alignment, are byte-identical to 012. Visual acceptance remains
pending. No installed game or save changes.

## Retained from 012

Fix the No alignment regression reported in the user's End Phase screenshot.
The previous spacer assumed 25px glyphs, but Rengoku's font preset uses 28px
glyphs with 25px character pitch, placing gray No nine pixels too far right.
The invisible spacer now tabs to the third native column using live pitch;
the existing slash and space place No at column five. Active label and cursor
positions stay unchanged. See [source evidence and tests](confirmation_alignment_012.md).

All six Yes/No variants match in tests executing native style selection and
the emitted pen-update code. The exact old adapter reproduces the nine-pixel
failure. All 100 tests, 172 rebuilt-member readbacks and three offline RPCS3
decryption checks pass. The shipped adapter matches the tested machine code.
ELF SHA-256: `130fac1da279ee28f65825f62541049caccd0b1af0619b4eb3175e3c63221478`.

Only EBOOT and regenerated stage encryption differ from 011. Stage plaintext,
all 76 other game files, glyph mappings, lookup text, translations and artwork
match 011. No installation or save changes. Visual RPCS3 acceptance is pending.

## Retained from 011

Five title-screen Library buttons now use English in the same Times Bold
treatment as Z3.1. Scenario Chart has an English heading and new dark
Purgatory Chapter background. Its independently drawn episode number and
quoted chapter name now translate for all 15 chapters. The longest title
fits in 732.375px at the native 36px width / 40px height style. See
[source evidence, previews and generation prompt](library_chart_011.md).

All 5,360 menu animation samples and all chart animation bytes are retained.
The final EFF comparison changes only members 131, 132 and 133; all 133 other
stored member payloads match 010. English logo, controls, nodes, connectors
and panel borders remain intact. Executable code and existing adapters are
unchanged; its lookup data expands to cover the separate chart strings.
ELF SHA-256: `53a4f5b78173dbd37be0c1fa6da27c292da87b6e02b6e5cccfeba00b4c265170`.
Stage plaintext remains unchanged from 010. All 96 tests and three offline
RPCS3 decryption checks pass. No game installation or save changes.

## Retained from 010

Both title-screen layouts use the same English gold wordmark as Z3.1 and a
new green **Purgatory Chapter** subtitle. The original animated Z frame and
fiery fills, backgrounds, prompt, menu buttons and animation records remain
byte-identical. Only two rectangles in EFF member 133 change, covering all
3,393 native wordmark/subtitle references. See [artwork, source evidence and
generation prompt](title_screen_010.md).

The final packed EFF has all 135 other stored member payloads unchanged
from 009. The executable and every other game file match 009, apart from
regenerated stage encryption whose plaintext is unchanged. Prior layout,
font, translation and link fixes are retained.

## Retained from 009

The inactive half of Ally / Enemy is dimmed, with both states using the
same size, baseline and row center. Five map-hover Spirit strips retain
their original 17 slots and status indices, using compact two-letter cells
instead of overflowing full names. Support, movement, Focus and recovery
labels fit their narrow fields. Six confirmation pairs retain native cursor
columns. The earlier claim of exact Yes/No alignment was disproved by the
user's screenshot and is superseded by build 012's correction above.
See [source evidence and tests](screenshot_layout_009.md).

There are 38 guarded FSSA record edits. Font mappings and previous masks
are preserved, and existing PowerPC adapters remain unchanged. New font
cells and lookup text produce ELF SHA-256
`d0c64ae7e6f02d215094de330694edf5dbb5e5e7b716584f79445c1a6db582f9`.
Stage plaintext still has SHA-256
`06e21b41ac0f21db9fc9ae56a98ccb4aa1e86acbe420fda3c47fc9cc5994b8c1`.

## Retained from 008

All eight System Settings tab states use Settings 1 / Settings 2, with
original sizing and styling. Six narrow Team-view support headings use
S. Atk / S. Def at 21px, centered in their original spans. The Move footer's
value block shifts right by 32px, leaving a 10px gap after the full-size
label while staying inside its strip. See [source evidence and tests](screenshot_layout_008.md).

Build 008 changed 17 guarded FSSA records and retained the executable from
007. These edits, previous Effect wrapping and runtime fixes remain in 009.

## Retained from 007

Search tabs/captions now use Spirits and Abilities. SP Cost appears once;
the real SP value column remains unchanged. The narrow ally-list columns
use Rpr. / Res. / Sup Atk / Sup Def, and both bottom Focus fields use Foc.
All 26 relocated labels retain native positions, colors and styles.

All 204 Spirit/pilot-skill Effect bindings (187 unique source descriptions)
wrap within 1,000px and two/three lines. Mind Resist now occupies two lines,
with every word and condition retained. No RPW mechanics or canonical text
changed. See [source evidence and tests](screenshot_layout_007.md).

## Retained from 006

All 32 opening/ending narration rows now fit between 96px side margins,
using 32x36 glyphs and the original 60px row pitch. Timings, commands and
wording are preserved. The missed four-line vertical terrain string now
uses one compact Air/Grd/Wtr/Spc cell per line beside the native ratings.
All 15 chapter title images and the single-digit, double-digit and final
episode animations are translated. Title images use Z3.1's Seurat recipe;
other text remains Rodin Bold. See [source evidence and tests](screenshot_layout_006.md).

## Link backgrounds in 004

The new screenshots of record `STGZ3REN_00004:00011` exposed separate native
background calculations that still used character counts. Build 004 captures
actual link widths, uses active render-record coordinates for dialogue
selection, sizes backlog and speaker-name backgrounds, and fixes scene and
translated-glossary matching. It adapts the complete Z3.1 approach after
checking Rengoku's own addresses and live registers. See
[the source evidence and regression checks](link_backgrounds.md).

Build 010 preserves this link-runtime implementation and the story's
decrypted content. Recheck Blue, Elgan and Reformists in dialogue and Back
Log, follow both term links, return, switch selections and change scenes.

## Screenshot corrections

| Reported screen | Implemented correction |
|---|---|
| Screen-size setup | Center translated strings using their rendered widths, fixing the help line's leftward displacement |
| Map COMMAND menu | Same width-based centering for labels; align Funds, Turns and Z Chips colons to the SR Points column |
| Character library | Wrap descriptions at 1,140px; keep Nick/CV aligned with a gap before values; fit the Face hint |
| Operation End | Translate the complete assembled heading, including Episode 1: Green Earth |
| Unit/Pilot Info | Normal-size MEL/RNG; Z3.1 compact Air/Grd/Wtr/Spc labels in physical fields and movement composition; use Foc in narrow fields |
| Pilot Info | Shorten the header to Spirits; enlarge Units and move it right; retain the centered tab heading and Focus placement |
| Pilot skills and Ace Bonus | Match levelled skill names; draw the full Ace Bonus heading once and blank its three physical continuation records |
| Weapon Info | Center the tab heading, use compact terrain labels, and translate the previously bypassed UTF-8 labels such as Weapon Name, Ammo, EN and upgrade headings |

These are guarded changes to Rengoku's own routines and fields. See
`tools/rengoku_ui_runtime.py`, `tools/rengoku_screenshot_layout.py`, and
[the source evidence for build 005](screenshot_layout_005.md).
Native numbers, level values, colors and game logic are preserved. The new
font changes line widths elsewhere too, so wrapping and bounds still need
playtesting. The screens must be rechecked in build 013 before calling
their appearance verified.

## Use

For RPCS3, select the complete `RPCS3/NPJB00689` folder with File > Boot Game.
Keep the existing game/license setup. No license is included in the build.
The original `DATA01.EDAT` requires your matching
`JP0700-NPJB00689_00-SRWZ3RENDLGPKG00.rap` in the emulator's
`dev_hdd0/home/<active-user>/exdata/` directory. Restart the game after installing
the license. Do not put licenses into patch ZIPs.

On the first user boot, RPCS3 reached graphics and asset initialization, then
reported `SCE_NP_DRM_ERROR_LICENSE_NOT_FOUND` (`80029521`) for `DATA01.EDAT`.
Its log named `E:/RPCS3/dev_hdd0/home/00000001/exdata/` as the missing license
directory. The matching 16-byte RAP already supplied in this project was
installed there and its readback verified on 2026-09-25. Game files and saves
were unchanged. Later user screenshots show successful gameplay and menus
in build 002, confirming the license error was cleared.

For PS3 with CFW/HEN, install and activate the matching original NPJB00689 game,
back up the matching files, and copy the contents of `PS3/NPJB00689` over
`/dev_hdd0/game/NPJB00689/` while the game is closed. Enable HEN if applicable.
The ZIP contains the same overlay. This task did not perform installation.

## Coverage and verified results

- All 3,334 canonical story records are inserted in rebuilt Lua literals.
- 39 SRVC banks contain 5,077 translated occurrences. All 6,356 cue pointers
  resolve to their expected strings; header bytes and unused source remnants
  are preserved. Other battle quote locations are covered by the text routes.
- Lua, library, indexed menu, FSSA, credit and metadata formats have guarded
  insertion paths. Defense/Defend occurrence overrides are retained.
- 173 CPK members across nine archives are rebuilt and read back. Every
  untouched member matches its original bytes. The encrypted stage decrypts
  exactly to the rebuilt archive.
- Rengoku-specific ELF patches add text storage, 122 font cells, proportional
  advance, centering, Unicode translation and keyword placement hooks. The original two LOAD segments, TLS,
  entry and process metadata are preserved. Edits require the exact source
  ELF hash and expected instructions; no sibling executable addresses are used.
- 11,768 exact source-to-English mappings are in the draw-time table, including
  324 levelled skill variants and 1,500 assembled chapter-heading variants. There
  are 3,539 other catalog occurrences relying on that table, plus 32 timed
  narration rows with measured layout. Actual rendering remains unverified.
- System dialogs use ordinary UTF-8; runtime placeholders and engine lookup
  keys retain their native bytes. English was not truncated to fit source fields.
- The NPDRM fake SELF retains source application/capability/title metadata.
  Complete game, PS3 overlay and ZIP contents match. All 104 tests pass.
- Five new tests execute the emitted PowerPC adapters, checking both text
  encodings, three font styles, register preservation, Japanese fallback,
  exact lookup, compact slots and fragmented Ace Bonus buffer reuse. These
  tests do not substitute for rendering in RPCS3.
- Eight link tests exercise every render slot, native name geometry,
  registration and active-record lookup, stale/null scenes, glyph widths,
  reused slots and the original offscreen-rectangle failure. The checks
  preserve native metadata and the live Rengoku style/draw context.
- Seven build-005 tests check the actual four Ace Bonus records, field bounds,
  library word preservation, normal stat labels, native movement fields,
  complete chapter headings and exact Z3.1 terrain masks.
- Six build-006 tests check all 32 narration rows and word streams, actual
  vertical FSSA fields, all 15 title texture pairs, all numbered episode
  quads, final-card rectangles and preservation of unrelated data.
- Five build-007 tests check search tabs/result captions, the split SP Cost
  heading, all narrow ally-list copies, source guards, every Effect word
  stream/line limit and both Mind Resist encoding paths. The final package
  was also reopened: all 26 labels and 187 effect hooks match the report.
- Four build-008 tests check all settings-tab states, narrow support-column
  gaps/centers, the composed Move footer, source guards and unrelated-byte
  preservation. The finished archive has all 17 edits and prior labels.
- Nine build-009 tests check both selection tints and geometry, the native
  tint path, Spirit slot indices and exact reference masks, narrow map
  labels, all six confirmation pairs and strict edit scopes. The final
  archive audit preserves every unrelated build-008 FSSA byte and existing
  font cell, chapter image and PowerPC adapter.
- Five build-010 tests check Rengoku's title constant and 3,393 native logo
  references, both settled layouts, all sampled Z rectangles, real alpha,
  the exact Z3.1 wordmark, source/art guards and unrelated-byte preservation.
  The large and small title-sprite compositions were visually inspected.
- Six build-011 tests check actual Library sample bindings, preservation of
  the English logo and unrelated bytes, chart controls/nodes, all 115 separate
  prefix/title lookup forms through the PowerPC adapter, native text bounds
  and rejection of incorrect source assets.
- Four build-012 tests check native confirmation font metadata, reproduce the
  previous nine-pixel error, align all six Yes/No pairs, and check 144 origin/
  pitch/quad combinations, register state and all ordinary glyph advances.
- Four build-013 tests reproduce the battle-preview overflows using actual
  font presets, fit all 15 captions and related variants, preserve colons and
  values, reject stale source data and compare unrelated bytes against 012.
- RPCS3 independently decrypted the pristine stage, rebuilt stage and new
  executable to the expected bytes. These are offline format checks; they do
  not prove that build 013 boots or that every text consumer accepts the edits.
- Original extracted files and canonical localization inputs are unchanged.

## Remaining validation

Boot and playtest RPCS3 and a real CFW/HEN PS3. Check menus, save/load, the first
stage, battle subtitles, library screens, credits, keyword links, substitutions,
typewriter timing, wrapping and text bounds. In particular, formatted or
fragmented draw calls may not match the whole-string translation table.

The remaining 166 cataloged artwork/manual blocks require image insertion. Raster
discovery is incomplete, and `DATA01.EDAT` remains opaque. The existing four
story, 54 battle and 97 non-dialogue review flags are unchanged.

## Reproduce

Requires the pristine local extraction, canonical catalogs, `requirements.txt`,
the recorded fonts and local tools. `build_game.py` reads the sibling's CPK
writer and fake SELF wrapper as tooling references; it does not invoke sibling
build/preparation scripts or write to that project. Executable addresses were
identified against this game's authenticated ELF. Binary assets stay ignored.

Choose a new output directory; existing builds cannot be overwritten. Inspect
the dry-run route report and pending cases before writing.

```powershell
python -X utf8 tools/build_game.py --out work/builds/rengoku_en_014
python -X utf8 tools/build_game.py --out work/builds/rengoku_en_014 --write
python -X utf8 tools/verify_game_build.py work/builds/rengoku_en_014
python -X utf8 tools/verify_game_build.py work/builds/rengoku_en_014 --write
```

The verifier creates a fresh `verification/` directory and runs only offline
decryption on copies. Sandboxed RPCS3 startup hung, including command-line help;
approved execution outside the sandbox passed all three checks in seconds.
Do not diagnose a timeout alone as a bad patch, or terminate unrelated emulator
processes. Build reports and verification evidence remain under the build folder.
