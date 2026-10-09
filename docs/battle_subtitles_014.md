# Battle-animation subtitle wrapping — build 014

The reported Blue subtitle crossed the status icons at the right of the
battle dialogue panel. The generated SRVC text had no width validation.

The generated subtitle is:

> 「Mass-produced or not,
> I can't let this get scratched!」

No words, punctuation, names, font masks or font sizes change. The canonical
English catalog and its source fingerprints stay untouched. The display
transform runs only while rebuilding SRVC banks; it preserves existing
fitting breaks and otherwise chooses a word boundary, preferring a clause.

## Evidence and bounds

- Screenshot: `codex-clipboard-f0820230-7d6b-4a7c-8613-86848ae4e460.png`.
  At the game's 1280px coordinate scale, the opening quote is approximately
  x276 and the right status panel begins approximately x1027. A 730px text
  budget ends at x1006, leaving about 21px clearance. These are measurements
  from the supplied capture, not native widget bounds recovered from code.
- Use the current Rodin Bold advance table at a conservative 32px quad.
  The captured line is consistent with approximately 31px quads. Before
  wrapping, its measured width is 861.22px at 31px, or 889px at 32px.
  The two new rows are 393px and 487px at 32px.
- Message `battle:bb4a3ab0560dceda`, source fingerprint
  `bb4a3ab0560dceda258f2d8fd5920017d6ad904da8ad2772d6cca751dd201a89`,
  occurrence `battle_occ:558760a00c4c7c6a9f5d`: Rengoku SRVC bank 19,
  cue index 103, original pool offset 147287.
- Rengoku routine `0x12c3b4` uses the literal `\n` delimiter at `0x878178`,
  reached via TOC pointer `0x94df44` (TOC `0x953f88`, displacement -0x6044).
  It searches, copies each segment and emits byte `0x0a`. The native glyph
  drawer recognizes LF at `0x14258`; `0x142f4` resets x to the row origin
  and advances y by the native line pitch. No new executable hook is used.
- Source battle subtitles already contain one explicit break. This change
  retains the two-row maximum. Actual font style/line pitch and visual fit
  across other animation layouts still need in-game verification.
- Initialization at `0x12c078` clears a 0x86-byte subtitle buffer at object
  +0xfb3; state follows at +0x1039. Every changed entry, after native escape
  conversion including NUL, fits this buffer. Blue's result takes 110 bytes.

## Scope and remaining work

The layout audit examines 3,558 unique SRVC messages (44 full 80-record
slices and a final 38), covering 5,077 stored occurrences. It changes 464
unique messages / 609 occurrences. This is a word-preserving layout audit,
not a new meaning review. No terminology choices or spellings change.

Forty-five existing over-width messages require separate handling and stay
unchanged in this build. They include long save/quit conversations and
battle lines exceeding the native intermediate buffer. Do not condense them
to a byte budget: relocate their text storage and verify the appropriate
consumer before applying wrapping. `SUBTITLE_LAYOUT.json` in the build lists
all changes, measured widths and each pending ID. This is a known remaining
limitation; build 014 does not claim complete subtitle coverage.

## Validation

All 108 tests pass. The four new tests check the reported Blue line, every
changed word stream and width/capacity, all 6,356 cue readbacks, and execution
of Rengoku's real escape-conversion instructions with CRT call fixtures.
The converter emits LF and leaves a canary after its destination intact.
All cue metadata and order stay unchanged. Previous No, map, menu, artwork,
font and battle-preview regression checks remain in the suite.

All 172 archive-member readbacks pass. The complete RPCS3 folder, PS3
overlay and ZIP hashes agree. Three independent RPCS3 offline decrypt
checks accept the original stage, rebuilt stage and English executable,
with byte-identical decrypted output. Only SRVC and regenerated stage
encryption differ from 013; executable, AID, artwork, font mapping and
stage plaintext match. Original sources and canonical catalogs are intact.

The overlay ZIP is 75,826,869 bytes, SHA-256
`ff94c20e434a12b8313092d2a3fc270c47107cdeb3abd8123f1025a0b610beb6`.
The complete 78-file folder and matching 12-file overlay are under
`work/builds/rengoku_en_014/`. Previous builds and installed games are intact.

This evidence is offline validation. It is not a captured gameplay result.
Test build 014 in RPCS3 at this same animation, including two-line quotes and
both factions' status panels. Real PS3 execution also remains unverified.
