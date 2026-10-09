# Rengoku dialogue and backlog link backgrounds

The user reported oversized Blue/Elgan backgrounds and a Reformists highlight
off the right edge in build 003. The scene is canonical record
`rengoku:STGZ3REN_00004:00011`, whose links are Elgan then Reformists.
The text already used Rodin Bold and measured
advances. The background consumers still used Japanese character counts.

`tools/rengoku_link_runtime.py` ports Z3.1's approach, using Rengoku's own
authenticated executable and independently disassembled sites. The reference
implementations are the sibling's `link_background_layout.py`,
`main_link_background_layout.py`, `link_identity_geometry.py` and
`dialogue_link_scene.py`. The sibling is read-only; no addresses are copied.

## Rengoku consumers and fixes

| Consumer | Native site (virtual address) | Correction |
|---|---|---|
| Linked text registration | `0x21a4cc` | Capture the actual floating-point pen advance into the allocated slot's width cache |
| Secondary/backlog selection | `0x21412c`, `0x2141c0` | Select that slot's cached width and preserve it across style calls |
| Primary dialogue selection | `0x212244` | Match active render records by scene and glossary index; use their signed X/Y and measured width |
| Registration scene | `0x21a4f4` | Retain explicit backlog context; null dialogue context falls back to scene zero |
| Registration comparison | `0x21a564` | Compare exact translated forms before native glossary-index assignment |
| Speaker-name widget | `0x2a7348` and guarded float-conversion sites | Measure the displayed name at the widget's quad width; retain native fallback for unknown text |

Rengoku keeps the primary style/draw context in r28, while the Z3.1 helper
assumes r27. The adapted helper preserves r28 and uses r27 as its slot counter.
Native primary conversion scratch is at stack +0xa0; secondary width scratch
uses the independently checked unused +0x88 slot.

The cache is 256 floats at `0xcea000`, within the build's mapped, initially
zero-filled scratch space. Existing glyph widths and joined-heading state
remain separate. Helpers are placed by the existing guarded code allocator,
below the glyph-width table. There are no new ELF segments.

Link record layout remains 20 bytes; native registration still owns source
length, style, active flag, scene, glossary index and navigation data. Width capture replays
the original length-byte store and writes only the separate cache. Primary
selection uses the real active-record getter; stale scenes, mismatched IDs
and inactive entries cannot supply its rectangle. The original primary Y+1
inset, heights, colors and drawing tail remain in use. Speaker geometry keeps
the existing X/Y, height and navigation fields.

## Verification

Eight focused tests execute the generated PowerPC and relevant native code.
They cover every render slot, slot reuse, bounded invalid selection reads,
signed coordinates, active-record lookup, wrong/null scenes and glossary IDs,
volatile register clobbers, metadata isolation, glyph advances at multiple
sizes, and speaker-name fallback. Registration tests begin before scene
assignment and pass the native result through primary selection for both
Elgan and Reformists.

One regression test executes the original arithmetic: an English link at
column 34 becomes X=1286 with width 310 on a 1280-wide canvas. The replacement
uses the fixture's actual rendered X=678 and width 145.25. A separate test
reproduces the oversized Blue name box before the fix. Six complete native
blocks, individual patched instructions and the full source ELF are guarded.

These are CPU and binary checks, not captured rendering. Recheck both adjacent
terms and Blue in dialogue and Back Log, switch between entries, follow each
link and return, then change scenes. No dialogue wording or source link order
was changed. The build still needs this in-game visual confirmation.
