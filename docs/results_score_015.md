# Battle-results kill count — build 015

The screenshot `codex-clipboard-809c3895-5777-44c0-8505-9b08c383bbf0.png`
shows Blue's score of 13 with a translated “Units” suffix extending into
the Level column. The source uses 機, a machine counter, beside its score
widget. The nearby source label 撃墜 identifies this as a kill count.
The number is game state; this patch does not change its calculation.

The results column now reads **Kills** with a bare numeric total. Its
neighboring Level remains separate. Pilot Info keeps the full-size “Units”
suffix requested earlier.

## Source bindings and scope

All offsets below belong to Rengoku's AID member 0, source SHA-256
`2432b3425ef264a10a311a6707f7963acd1cbe802868b07b702a51d9c62e8ad0`.

| Record | Source | Display |
|---|---|---|
| `0x99ce4` | Ｓｃｏ | Kills |
| `0x99d04` | ｒｅ | Empty; continuation of the same heading |
| `0xa6fe4` | 機 | Empty; compact score suffix |

The two heading fragments precede Ｌｖ at `0x99d24`. Their original
28px preset, positions and colors stay unchanged. Kills clears the Level
heading with more than 12px spare. The original header group contains
the consecutive references at `0xe4fac..0xe4fb7`.

The compact score group at `0xfa3ac` references two numeric placeholder
records (`0xa6fa4`, `0xa6fc4`) and this suffix. Its three text references
at `0xe8f18..0xe8f23` are unchanged. Only the suffix's text pointer changes;
its style, placement and all live counter fields remain intact. Shared
uses of this compact widget also lose the redundant suffix.

Pilot Info uses a different record, `0x8f044`, whose “Units” wording and
build-005 size/position correction remain intact. The other three 機
records at `0x99344`, `0x9b404` and `0x9b424` also remain unchanged.
No global translation of 機 is changed.

Reviewed FSSA slices 2080–2159 and 3840–3919, with five neighboring
records on each side: 160 in-slice records, 180 examined. Three display
records change. “Kills” reuses the existing project label for 撃墜数;
no terminology question or canonical translation change remains.

## Validation and remaining checks

Focused checks verify the actual source groups, header clearance,
untouched live fields and all four other Units labels. Comparison against
build 014 permits only three string-pointer changes and 13 appended bytes
in AID member 0. Stale source labels are rejected.

All 110 tests and 172 archive-member readbacks pass. The finished complete
folder, PS3 overlay and ZIP hashes agree. Three RPCS3 offline decrypt checks
accept the original stage, rebuilt stage and English executable and return
byte-identical plaintext. Packed AID comparison changes only member 0;
all 15 other members match 014. The executable, SRVC, font, artwork,
canonical catalogs and stage plaintext are unchanged.

Build outputs: `work/builds/rengoku_en_015/`, 78-file complete RPCS3 folder
(614,528,313 bytes), matching 12-file CFW/HEN overlay and 75,826,879-byte ZIP.
ZIP SHA-256: `286864394316d989aeab947ff8c84f06ac3118a2e5eb43b5ec9d879b204775d2`.

The result still requires an in-game check with one- and two-pilot result
rows and larger totals. Offline checks do not establish final visual fit
or real PS3 compatibility. Prior builds and source data remain intact.
