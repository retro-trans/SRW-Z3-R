# Honorific context and battle-caption buffer correction

Reported 2026-11-24: Setsuko uses bare Advent/Blue before their replies grant
permission to drop honorifics; long battle subtitles end mid-sentence and
the accompanying name/portrait can disagree.

## Story context

Three STG00015 records now retain Mr. before the name: 00015 (both Advent
and Blue), 00025 (Blue), and 00036 (Blue). Advent grants permission at 00016;
Blue does so at 00037. Later bare-name address is unchanged. Review examined
rows 0–79 plus 80–83 context: 84 examined / 80 in-slice. All glossary refs,
wrappers, line counts and source fingerprints are preserved. There are no
unresolved honorific choices. Expanded lines pass the native-font 870px bound.

## Native battle defect

NPJB00689's converter at VA0x12c3b4 changes literal backslash-n into LF.
Its callers store the result at object+0xfb3 in a 0x86-byte field. Portrait
state immediately follows at +0x1039 and +0x103c. The animation UI also makes
a fixed 0x86-byte copy at VA0x14800c. Previous builds inserted English atlas
text directly into SRVC; each Latin letter takes two bytes in this codec.
The pre-correction scan found 92 stored English occurrences over capacity.

The three distinct reported captions require 160, 152 and 142 bytes after
conversion including NUL, exceeding 134. Executing the original converter
with those English strings overwrites canaries in the following portrait
fields. The fixed-size UI copy also loses sentence endings. This is a
memory-layout defect, not a reason to guess speaker identities from portraits
or numeric bank IDs.

The new route preserves SRVC byte-for-byte, including all 39 banks and 6,356
cue indexes/metadata. Native Japanese passes through every small field and
conversion unchanged; its maximum converted size is 127 bytes including NUL.
English is resolved only in owned draw-time storage using the complete
converted Japanese key. All 5,077 source occurrences / 3,558 unique keys are
covered. No new executable addresses from the sibling or manual portrait/name
overrides are used.

Instruction-level tests execute the real converter and the patched draw
entry for the three reported lines: Japanese remains within capacity, the
following state stays intact, and the draw pointer resolves to complete
English outside the object. This proves the tested code paths offline;
appearance, timing and state transitions in a running game still need testing.

## Complete caption category

Word-preserving reflow now runs outside the native byte limit at a
conservative 32px Rodin quad, two rows of at most 730px. Seventeen remaining
over-wide entries received source/context-reviewed concise wording, including
save/quit announcements. None of the reported three battle lines was reworded.
Controls, wrappers, glossary references and source IDs/fingerprints remain.

Meaning review A: 8 targets + 25 distinct context rows = 33 examined, within
two 80-row containers (160 structurally scanned). Review B: 9 targets + 39
context = 48 examined, within seven 80-row containers (560 structurally scanned).
Unrelated container rows were not claimed as meaning-reviewed. Established
Reactor, Beater Service and Chrono terms remain; ops abbreviates operations.
No new unresolved meaning choices; inherited review flags remain intact.

The mechanical layout scan covers all 3,558 unique SRVC messages in 44 complete
80-record slices plus 38. Source, glossary/control checks and the idempotent
honorific/caption fixers pass. Word-preserving reflow changes 508 unique
display entries / 662 occurrences; no width cases remain pending. After the
17 concise wording edits, 91 entries would still exceed the old native byte
capacity, so they require the owned-storage route even when their rows fit.

## Completed local build

Build030/v0.9.2 retains the audio/settings corrections. All 20 focused battle
tests pass, including original cue preservation, real converter/lookup
execution, source/control guards and prior battle-preview layout tests.
The packed executable resolves all 5,077 occurrences / 3,558 unique converted
keys to the complete expected English. All three honorific corrections are
present in the packed STG00015. Previous 36 audio-caption and 296 operation
lookup checks pass. Every archive, complete folder, overlay and ZIP agrees;
the packed bottom-left title footer is v0.9.2 / github.com/retro-trans.

Three independent RPCS3 offline decryptions exit 0 and produce exact expected
data. Local package and isolated installation match all 77 expected files.
Package: `work/runtime_pkg_092/SRW-Z3-R-NPJB00689-English-build030-RPCS3.pkg`;
725,584,976 bytes, SHA256
`6cc0f9825744b1d4960f798dbb2be7bb7a327367bddb1a8a3a02e8c827f85cc4`.
Proofs: `work/battle030_packed_check.json`, build verification/RESULT.json,
`work/runtime_pkg_092/PKG-VALIDATION.json` and
`work/rpcs3_pkg_092/INSTALL-VALIDATION.json`. The known native installer
teardown assertion 3221226505 is distinct from successful file checks and is
not a game boot result. Original package/extracted data, old builds and
published assets are preserved. Source audit verifies 77 files, 122 CPK
members, 95 Lua members and 3,334 records; it selects PS3 NPJB00689 explicitly
when a separate Vita PKG is also in the workspace.

This package is RPCS3-only and local, not a new public release. Next complete
build is 0.9.3. Restart RPCS3 and load an in-game save before retesting; old
emulator save states can retain earlier resources and corrupted state.
Gameplay, portrait selection, timing and physical PS3 execution remain
unverified. Public v0.9.0 is unchanged.
