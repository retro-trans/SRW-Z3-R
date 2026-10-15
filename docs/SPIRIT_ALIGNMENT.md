# Spirit Command alignment — 2026-10-15

Compared the read-only sibling's canonical English `spirits` and `spirit_hook`
catalogs by Japanese identity, rather than by translated name or numeric slot.
The comparison hashes and all rows are in `analysis/spirit_alignment.json`.

- Examined all 14,073 English locale records, including the 1,168 imported
  glossary entries. Found 42 shared command identities across 87 name entries.
- Two mismatches: 直撃 was Fury in Rengoku but Break in Z3; 闘志 was Fighting
  Spirit in Rengoku but Fury in Z3. The selected command in the supplied
  screenshot is 直撃, whose effect ignores size/all-target damage penalties
  and defensive abilities/skills. Its aligned name is **Break**.
- Updated 10 source-bound entries: three full command-name entries, two
  one-character status labels, two status-strip descriptions, a multiline
  command list, Bravery's component list and a deployment-bonus description.
  The 18 native status cells retain Japanese identity/order; 闘 now shows Fu,
  and 直 shows Br. Native slot size, highlight index and placement are retained.
- The other 40 shared names already match, including Focus+, Intuition,
  Bless, Mercy, Guard/Guard+ and Wall/Wall+. Hope and Revival are present only
  in the sibling's name catalog; no matching name entry was found in Rengoku's
  current catalog. This is not proof of their absence from every game asset.

Compared 37 effect entries with identical Japanese source. After the Bravery
terminology correction, 32 match word-for-word apart from whitespace. Five
retain Rengoku's existing wording: final hit/evasion, Break's defensive
abilities/skills, Accel's movement, and the two team HP recovery descriptions.
No effect, value, target, duration, SP cost or game mechanics were changed.
The unrelated 戦意高揚 pilot skill remains Fighting Sp; ordinary prose about
fighting spirit is preserved. No dialogue meaning was rewritten.

`tools/align_spirit_terms.py` defaults to an inspected dry run; the applied
pass changed only the displayed 10 entries. A repeated preview makes zero
changes. Four focused terminology/identity/idempotence tests and all nine
existing build009 layout tests pass, including generated status glyph masks,
native strip slots and highlight order. Canonical non-dialogue/source bindings
and story/glossary validation pass. Generated reading copies are refreshed.
AGENTS.md retains the distinction for future edits.

The initial audit changed sources only. The subsequent release build026/v0.1.5
includes these corrections: all 42 command lookups and five packed status
strips pass compiled-data readback, and all 77 package/installed file hashes
match. See [0.1.5 validation](validation/0.1.5.md). Public v0.1.2 retains its
prior names. In-game verification is still pending; source/binary checks are
not proof of the supplied screen's corrected appearance. The sibling and
original assets are intact.
