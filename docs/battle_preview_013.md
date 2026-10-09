# Battle-preview caption overflow — build 013

The user's screenshot shows overlapping weapon-cost labels, Focus labels
touching the values on both factions, and Attack clipped beneath the central
target arrow. These are separately positioned FSSA records, not one sentence
that can be fixed by wrapping.

## Source and sizing

All edits target this game's AID member 0. Its font presets come from AID
member 4, table `0x488`, with 13 entries. Preset 2 draws 25px glyphs, preset 4
draws 23px glyphs, and preset 9 draws 37px glyphs. These dimensions differ
from some character-pitch bytes in the records; build 012's distinction
between glyph size and pitch is retained.

The ammo caption at `0xa70e4` starts at native x=639.5; its colon at
`0xa7104` starts at x=696.5, leaving 57px. English Ammo Remaining exceeds
that span. EN and Use are separate records at x=639.5 and 673.5, followed
by a colon at 708.5. Use alone advances 43.125px, ending at 716.625 and
crossing the colon. The screenshot shows both factions reuse these widgets.

The two Focus records are `0xa03e4` and `0xa0424`. At the real 25px preset,
Focus advances 74.21875px, exceeding the roughly 56px label/value space.
The 37px Attack badge advances 115.625px against a roughly 94px badge.
Those limits come from the supplied native-scaled screenshot; in-game
acceptance is still necessary.

## Caption changes

| Field | Display | Width | Available span |
|---|---|---:|---:|
| Ammo remaining | Rnd. | 52.469px | 57px before colon |
| EN consumption | EN | 32.344px | 69px before colon |
| Song EN consumption | S.EN | 55.344px | 87px before colon |
| Focus, both factions | Foc | 45.313px | 56px before value |
| Attack, both shared variants | Atk. | 72.844px | 94px badge |
| Defense badge | Def. | 76.313px | 94px badge |
| Support defense badge | S.D. | 77.469px | 94px badge |
| Support attack title | S. Atk | 66.844px | 96px before counter |
| Support defense title | S. Def | 69px | 96px before counter |
| Second attack title | Re-Atk | 77.625px | 96px before counter |

The three redundant cost fragments are blanked in their display records;
the original colon and live numerical values remain. Charges already fits
its 100px span and is checked without changing it. Counter, evade and wait
badge variants are also checked and retain their existing English.

Z3.1's `tools/battle_preview_layout.py` supplied the compact-label approach
and terminology. All record offsets and font presets used here were found
in Rengoku. No executable addresses or game data are copied from Z3.1.

Fifteen string pointers change. All position, font, pitch, color, alignment,
animation and value records are preserved. The full text in the canonical
catalogs is unchanged. The displayed abbreviations are local to these
widgets and do not replace dialogue or full descriptions.

Review scope: two 80-record context slices (`0xa0184..0xa0b64` and
`0xa6ba4..0xa7584`) plus nine adjacent records around the other Attack
variant, for 169 examined records and 15 edited captions. No unresolved
terminology choices; S.EN means Song EN and S.D. means support defense.
Remaining uncertainty is the final in-game appearance of these variants.

## Checks

Four focused tests reproduce the prior overflow using actual font presets,
check corrected captions and shared variants, verify colon/value clearance,
reject stale source presets, and compare every other byte with build 012's
FSSA. These are offline asset/measurement checks, not gameplay captures.

Build 013 is complete under `work/builds/rengoku_en_013/`. All 104 tests,
172 rebuilt-member readbacks and three independent RPCS3 offline decrypt
checks pass. The complete RPCS3 folder has 78 files totaling 614,528,297
bytes; the PS3 CFW/HEN overlay contains 12 files. The ZIP is 75,826,207
bytes, SHA-256:
`9041744285decff3a8d1ad3cdb9bc25ead7b9993263d5eecda0f7ce75ae6decd`.

The packed audit confirms only AID member 0 changes: exactly the 15 string
pointers and appended labels. All other 15 members match 012. All other
game files match except regenerated stage encryption; its plaintext is
unchanged. The executable is byte-identical to 012, preserving its No-tab
fix. ELF SHA-256:
`130fac1da279ee28f65825f62541049caccd0b1af0619b4eb3175e3c63221478`.
Original assets, canonical catalogs, installed games and saves are unchanged.

Recheck both faction orientations, known/unknown values, ammo/EN/charge
weapons, support slots and action choices in RPCS3. Real PS3 rendering also
remains unverified.
