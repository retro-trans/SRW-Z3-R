# Battle fast-forward prompt — build 016

The screenshot `codex-clipboard-953576bf-f286-43bc-925e-37d8fc7e52ae.png`
shows Fast Forward extending behind the Cancel button icon in the short
battle display. Both matching prompts now read **Fast** at their existing
font size. The full translation in the canonical catalog remains unchanged.

## Source and fit

Rengoku's AID member 0 has two physical records for `：早送り`:
`0x8c2e4` uses preset 4 (23px), and `0x8c944` uses preset 6 (21px).
The latter is adjacent to the matching `：キャンセル` at `0x8c964`.
The style dimensions are verified against this game's AID member 4,
not inferred from the text records' character-pitch bytes.

The compact display `：Fast` fits inside the original four Japanese cells
with at least eight native pixels reserved. No button icon, Cancel text,
font size, position, color, alignment or animation record changes. Only
the two text pointers and their appended display strings differ.

Reviewed the 80-record slice 400–479 with five adjacent records on each
side: 90 records examined, two display labels edited. Both exact matching
prompts are covered. Fast is a contextual abbreviation of Fast Forward;
there are no unresolved terminology choices or dialogue changes.

## Validation scope

The build checks original labels, preset indices, exact font dimensions,
caption width and unchanged non-pointer bytes. Package comparison against
015 verifies the two pointers and 22 appended bytes in AID member 0 and
preserves the other 15 AID members.

| Record | Native quad | Caption width | Budget after reserve |
|---|---:|---:|---:|
| `0x8c2e4` | 23px | 71.156px | 84px |
| `0x8c944` | 21px | 64.969px | 76px |

All 110 tests and 172 archive-member readbacks pass. The complete folder,
overlay and ZIP hashes agree. Three independent RPCS3 offline decrypt
checks accept the original stage, rebuilt stage and English executable
with byte-identical output. Only AID and regenerated stage encryption
differ from 015; executable, SRVC, font, artwork, stage plaintext and
canonical inputs match.

Outputs are under `work/builds/rengoku_en_016/`: 78-file complete RPCS3
folder (614,528,329 bytes), matching 12-file CFW/HEN overlay and
75,826,880-byte ZIP. ZIP SHA-256:
`76df61ad0e847d2924729c28f52889428827e293620e878c0cc392871acdae60`.
The packed comparison is logged in `work/build016_comparison.log`.

Final in-game appearance still needs checking in both battle orientations.
Offline validation does not establish visual acceptance or PS3 compatibility.
Existing subtitle and artwork/manual limitations remain unchanged.
