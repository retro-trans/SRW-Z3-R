# Generated skill bonuses, rewards and carryover — 2026-11-24

The seven supplied screenshots cover four related categories. Canonical
translations are already correct; source-bound runtime/display adapters cover
generated strings and fit the native panels without changing gameplay values.

- Skill bonuses: cover bare `NAME +1` through `NAME +9`, including fullwidth
  glyphs and padding, for every existing level-bearing skill family derived
  from the source catalog. Keep existing level and level-plus-bonus forms.
  The reported Ignore Size, Support Atk and Support Def forms now resolve.
- Bonus reward: the native executable composes `金塊　` with an amount.
  Match that guarded prefix after composition, validate the complete decimal
  suffix, and encode Gold Bar plus its actual digits into an owned 128-byte
  buffer. Preserve leading zeros and quantities; support ASCII/fullwidth
  digits and padding. Nine/ten-digit amounts use Gold to fit the column;
  a separately drawn prefix uses Gold to fit the native label span.
  Reject unrelated or malformed suffixes without modifying source memory.
- Carryover: audit both with-Z-Chips and no-Z-Chips variants, including the
  latter's two indexed strings. Use a compact Carryover heading, shorter
  complete prose and labels, separate percentage columns, and remove four
  redundant static colored text copies. Preserve the live 50/75/100% fields,
  styles, row spacing, 15-level unit AND weapon limit from run four, five
  Power Parts per completed run owned at clear, cap 25, and Emblem exclusion.
- Final SR Point: retain the original Lua literal's explicit `ポ\イント`
  spelling. Add its observed runtime form `ポイント` to the draw lookup and
  all three generated numbered variants. This is a guarded single-literal
  alias, not a general rewrite of Lua escapes or original stage tables.

Meaning review consulted 12 target meanings plus 37 distinct context rows.
Four 80-record containers plus 16 boundary rows were structurally examined
(336 records). No unresolved terminology choices or canonical edits remain.
The inherited source IDs, fingerprints, glossary references, review status,
gameplay quantities and original package/extraction remain intact.

Verification: five focused checks exercise emitted PPC code, registers/CR,
source immutability, buffer canaries, maximum amounts, malformed inputs,
both carryover variants and indexed readback. Regression checks cover links,
build safety, battle captions, operations and audio/settings. The read-only
`tools/check_category031_build.py` verifies packed resources and executes
the final compiled lookup. All 37 focused/regression tests pass. Build031
v0.9.3 has zero pending insertions; 7,290 packed bonus forms across 15 skill
families, 17 carryover records, two no-Z indexed records, four final SR forms
and eight emitted PPC cases pass. Prior 5,077 battle captions, three
honorific corrections, 296 condition forms and 36 settings captions pass.
Archive/overlay/ZIP hashes, packed version/credit and all three native
offline decryptions also pass. Package/install results are in HANDOFF.
Offline checks do not establish in-game appearance or physical PS3 behavior.
