# Intermission, Pilot List and training layout — build 018

The three user screenshots show the Japanese Intermission heading, menu
fragments and redundant counter suffixes overflowing the Intermission
screen, Melee/Defense overlapping adjacent Pilot List columns and footer
values, and overlapping training tabs and PP labels.

## Display corrections

- Insert the canonical English Intermission heading into its native word
  sprite, using the same Rodin Bold recipe as the read-only Z3.1 reference.
- Join Team Setup and D-Trader into single centered menu captions, with
  blank continuation fragments. Both selected and inactive states retain
  their native colors. Parts leaves room for the existing NEW badge.
- Join SR Points and Z Chips, and remove the repeated Teams/Ships suffixes
  after deployment totals. Labels preceding those totals remain intact.
- Remove Units from all three Intermission kill totals. The first-place
  counter shares a suffix with Pilot Info, so **Pilot Info also shows a bare
  kill count**. Its prior font and position settings remain. This supersedes
  the earlier preference to enlarge that suffix; the shared side effect was
  explained during the work, with no preference reply received.
- Use MEL and DEF consistently in these Pilot List and training fields.
  Move the footer stat labels 10 native pixels left, retaining the live
  values and existing font sizes.
- Join all four training tab states as Raise Stats and Learn Skills.
  Replace the overlapping PP fragments with PP Held, PP Cost and PP Left
  at the original three row positions.

These are display abbreviations and grouping changes. Canonical English,
source IDs, source fingerprints, runtime substitutions and story wrappers
are unchanged. The source-bound review covers nine consecutive 80-record
slices: 720 in-slice records and 780 unique records including adjacent
context. There are 62 label overrides and 20 footer shifts. MEL/DEF reuse
existing terminology; the artwork heading uses its existing canonical
translation. No unresolved meaning or spelling choices were identified.

## Rengoku source binding and bounds

Only AIDDATAPACK_R.CPK members 0 (FSSA) and 1 (GTF artwork) change. All
addresses below were located in Rengoku, independently of the sibling.
Source strings and native styles are checked before any mutation.

Training tabs start at FSSA `0x96c24`, in four 128-byte groups. The complete
captions center on x727.5 and x995.5 with a 220px width limit. PP labels use
`0x9e304`; the duplicate PP draws at `0x9e324` are blanked. Their native
64px line spacing stays intact. The shared first-place/Pilot Info suffix
is `0x8f044`; the other score suffixes are `0x9b404` and `0x9b424`.

At 28px, MEL occupies 59.5px against a 72px header interval (12.5px spare).
At 25px in the shifted footers, MEL leaves at least 8.875px and DEF at least
7.219px before conservative numeric anchors. At 36px, training MEL and DEF
occupy 76.5px and 73.125px within their 80px spaces. No font shrinking is
used. Joined menu captions adopt the source's complete-caption placement
and alignment fields while preserving each state’s color.

The Intermission word cell is `(0,192,296,40)` in member 1's first 512×512
swizzled ARGB32 texture. Source member SHA-256:
`db7ef062281e0f8f5ce7b72eb7d56db8ae2948ad673d8d4b9d61931c9c64a6a6`.
The five source vertices at FSSA `0x4b95c` sample that cell and retain their
304×40 quad and 8px shear. The new white Rodin glyph mask is centered within
the cell; native tint and animation remain. Every other pixel and texture
in the member is checked unchanged. The preview is an asset proof, not an
in-game capture.

## Verification and remaining work

All 118 tests pass. The four new tests cover actual source fields, tab and
menu centering, PP spacing, header/footer clearances, unchanged live fields,
and the swizzled atlas round-trip. They were rerun after adding the explicit
native heading UV guard. All 173 rebuilt-member readbacks and three offline
RPCS3 decrypt checks pass. The build's `verification/RESULT.json` records
`all_passed=true`, with complete folder, overlay and ZIP hashes agreeing.

Packed comparison against 017 changes only the listed FSSA fields and
appended text in AID member 0, and the word cell in member 1. The other 14
AID members, all other rebuilt archive plaintext, executable and font match.
Only AID and regenerated stage encryption differ among the game files.
The Intermission asset proof was inspected; source data and catalogs match.

Outputs are under `work/builds/rengoku_en_018/`: 78-file complete RPCS3 folder
(618,373,897 bytes), matching 12-file CFW/HEN overlay, and 75,776,024-byte ZIP.
ZIP SHA-256:
`4e41693ce38e0cef445275af637b0d33b13cdb117a7daee2b12405f438bb3bd2`.
ELF SHA-256 (unchanged from 017):
`baa83a9cb2ebb54477df3155322a233f55975d9185d29d29b8cfd9c066cdb549`.
Logs: `work/build018_tests.log`, `work/build018_focused_tests.log`,
`work/build018_dryrun.log`, `work/build018_write.log`,
`work/build018_comparison.log`, `work/build018_verify_dryrun.log` and
`work/build018_verify_write.log`. The full review is `INTERMISSION_REVIEW.json`
inside the build; `intermission_heading_preview.png` shows the inserted cell.

Visual acceptance in RPCS3 and execution on a real PS3 remain pending.
Check the Intermission menu states, all three score ranks, deployment totals,
Pilot List pages and training tabs with the user's saves. Alternate final
chapter Intermission summary fields were examined but are outside this
three-screen correction and retain the previous build's formatting.
The 45 longer subtitle entries and 166 remaining artwork/manual blocks are
still pending. Originals, older builds, the sibling, installations and saves
are preserved.
