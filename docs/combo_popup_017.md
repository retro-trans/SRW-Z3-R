# Combo map popup — build 017

The user's `codex-clipboard-225e7ab4-44d1-4283-8aca-6c22fba7b466.png`
shows a very small Combo +2 popup inside the map cursor. This label already
exists in English in the original game. No translation or font replacement
is needed: the issue is the popup's draw scale.

## Rengoku source binding

TPACKPS3.CPK member 2, texture 6 is the native 80 × 400 ARGB32 strip with
five 80 × 80 cells: Combo +1, +2, +3, +4 and MAX. Member SHA-256:
`93955de0c34e65aa41a44a476c8b05d6b5ffa763200f0f4d70ae8e8bac22e6d4`.
The atlas remains byte-identical. Five artwork states were examined;
no translation records or terminology were changed.

These are independently located **Rengoku** virtual addresses:

- `0x3a4fb8` enters popup state `0x35` after choosing the Combo frame.
- `0x3a4688–0x3a46ac` selects texture 6 for state `0x35`; the other
  shared path uses texture 5 (Multi Action).
- `0x3a4640` loads the animated popup scale. `0x3a4644` loads map zoom.
- `0x3a46b4` multiplies those values and passes the result as `f4` to
  the shared quad drawer at `0x3a0e44`.
- The shared drawer at `0x3a0ef0` applies map zoom again, then multiplies
  by `f4` at `0x3a0f24`. Thus the original popup shrinks with zoom squared.
- The caller's `tile * 64 + 32` coordinates establish a 64-unit map tile.
  The shared drawer uses a 40-unit half-size and an 80-pixel UV stride.

## Correction

`rengoku_combo_runtime.py` replaces only the Combo state's caller scale
with `0.8 × animation_scale`. The shared drawer still applies map zoom.
The complete popup quad therefore spans one 64-unit tile at full size,
stays centered and scales once with the map. At zoom 0.5 this makes the
label 60% larger in each dimension; it also avoids oversized text at close
zoom. Transparent padding keeps the actual lettering inside the tile.

The adapter preserves all general registers, condition fields and LR;
only the intended `f4` output changes. Other popup states execute the
original instruction. Frame selection, +1/+2/+3/+4/MAX artwork, colors,
alpha, positions, animation timing, UVs and shared map drawing stay intact.

## Validation

Four focused checks pass: execute the shipped adapter with the native
quad-size instructions across eight zoom factors and six animation sizes;
reproduce the original double-zoom behavior; check other states and live
register preservation; reject changed source instructions; and validate
all five cells of the original atlas. These are instruction-level and
asset checks, not an in-game screenshot.

All 114 tests and 172 rebuilt-member readbacks pass. The link regression
now checks its own required adapters instead of assuming the executable
can never gain another adapter. Comparison against 016 allows only the
four-byte branch at `0x3a46b4` and the new 84-byte Combo adapter; every
earlier adapter retains its address and bytes. All archive plaintext,
sprite artwork, fonts, AID, SRVC, source files and canonical catalogs match.
Only EBOOT and regenerated stage encryption differ among the game files.

Outputs are under `work/builds/rengoku_en_017/`: 78-file complete RPCS3
folder (614,528,329 bytes), matching 12-file CFW/HEN overlay and
75,826,968-byte ZIP. ZIP SHA-256:
`5879d19a2cd8d7056244c88f76270095965185b006076a4e20db4ab2c9b2fc9c`.
ELF SHA-256:
`baa83a9cb2ebb54477df3155322a233f55975d9185d29d29b8cfd9c066cdb549`.
Full folder, overlay and ZIP hashes agree. Logs:
`work/build017_tests.log`, `work/build017_comparison.log`,
`work/build017_dryrun.log`, `work/build017_write.log`,
`work/build017_verify_{dryrun,write}.log` and
`work/build017_verify_retry.log`.

All three offline RPCS3 decrypt checks passed with byte-identical output;
the build's `verification/RESULT.json` reports `all_passed=true`. The first
attempt stalled before processing even the untouched original in the
restricted runner. Its evidence remains in `verification_sandbox_timeout`;
the retry outside that runner passed all three cases using verification
copies only.

Visual acceptance of Combo popups in RPCS3
and execution on a real PS3 remain pending. Existing subtitle and
artwork/manual limitations are unchanged. No game installation or saves
were modified.
