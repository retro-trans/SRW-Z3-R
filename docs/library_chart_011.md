# Library menu and Scenario Chart — build 011

The five title-screen Library buttons now read Robot Encyclopedia,
Character Encyclopedia, Glossary, Sound Select and Scenario Chart. The
chart has an English heading and Purgatory Chapter background. Its episode
number and selected chapter title now resolve independently to English,
including all 15 chapters and the final-episode prefix.

This pass examined eight artwork labels (five buttons, two copies of the
chart heading and one background) and 15 existing chapter translations.
The chapter English is reused from the canonical non-dialogue catalog;
story dialogue and glossary identities are unchanged. No unresolved new
translation choices. Purgatory Chapter follows build 010's title treatment.

## Source evidence and insertion

- Rengoku's own Lua constants bind chart animations 130/131 to EFF members
  131/132 and title/menu animations 132/133 to EFF members 133/134.
- The Library animation lives in member 134, while its shared texture is
  member 133, GTF 0xecfe0, texture 5, 664x360. Five native rectangles cover
  5,360 normal/transition samples. Their positions, UVs, timing, button
  sprites, selection animation and existing main-menu English are retained.
- The font recipe follows Z3.1's Times New Roman Bold at 42px, rendered at
  four times resolution, with white lettering and a gray glow. Rectangles
  and sample counts were independently established for Rengoku.
- The menu mutation composes with build 010's English logo, preserving its
  entire texture and all native animated Z sprites. It does not replace the
  title-art mutation with an unrelated copy of the original member.
- Chart member 131 uses GTF 0x62c00. Texture 1 carries the heading and UI;
  texture 2 is the full background. Member 132, GTF 0x1a0, has a duplicate
  UI atlas. Only the heading rectangle (96,14,472,66) changes in each UI
  atlas. All node icons, connectors, controller icons and dialog borders
  remain byte-identical, as do all animation bytes before each GTF.
- The background is newly generated artwork matching the dark green/teal/
  violet palette, with subdued English lettering. No original game assets
  were uploaded. Its source is hash-pinned in `localization/library_chart.json`.
- The Rengoku chart routine at 0x1b8984 calls the episode formatter at
  0x1b8a20 and draws the prefix at 0x1b8a40. It fetches the title at
  0x1b8a54, formats `%s%s%s` with the Japanese book-title wrappers and draws
  the result at 0x1b8a94. These separate strings escaped the previous
  combined-heading lookup. New exact matches cover 99 numbered prefixes,
  the final prefix and 15 wrapped titles. The existing converted-Unicode
  adapter translates them after conversion; no new executable code hook.
- The native chart style is 36px wide and 40px high, verified through the
  0x1b8bf0 caller and 0x1bca18 style setter. Numbered prefixes stay below
  the native 214px title offset. The longest title is 732.375px, within an
  800px content limit. Lookup text remains outside original fixed buffers.

## Validation

The inspected dry run reports 172 rebuilt archive members and 11,768 draw
lookup pairs. All 96 focused tests pass, including execution of the existing
PowerPC Unicode lookup adapter for all 115 new complete-string forms.
Source guards reject incorrect resources. Byte-restoration checks prove
that all unrelated artwork and animation bytes are retained. Original
assets, the sibling project and prior builds are preserved.

The completed build has 78 files (614,528,185 bytes) and a matching 12-file
overlay. Its ZIP is 75,826,144 bytes, SHA-256
`96a851b7d4c14cab962ff1a191a22dbedf27d6ece2111e476c48a4e3dad28424`.
Three independent offline RPCS3 decrypt checks passed. Final packed audit
against 010 changes only EFF members 131/132/133, with all 133 other stored
EFF members identical. Existing executable code/adapters are unchanged;
the lookup table expands. ELF SHA-256:
`53a4f5b78173dbd37be0c1fa6da27c292da87b6e02b6e5cccfeba00b4c265170`.

Local previews are atlas/glyph compositions, not gameplay captures:

- `work/menu011_preview/library_buttons.png`
- `work/menu011_preview/flowchart_artwork.png`
- Build output `library_buttons_preview.png`, `chart_preview.png` and
  `chart_longest_title_preview.png`, alongside the retained title previews.

In-game Library selection/transitions, chart selection and chapter labels
still need checking in RPCS3. Real PS3 loading is not verified. This pass
does not reduce the separate 167 pending cataloged artwork/manual blocks;
these newly located menu/chart sprites were outside that original catalog.

## Generated background provenance

Built-in `image_gen` was used, with no image input. The generated source was
copied into `work/menu011_source/flow_background_generated.png` and resized
only when packed into the native 1280x720 texture. SHA-256:
`4f8bcfc3dc70e4f2e3a6c7a41cb1425b1889307fcb6b3e8650da40ca04a6f37f`.

Final prompt:

> Use case: stylized-concept. Asset: a flat 1280 by 720 pixel 16:9 background texture for a science-fiction tactical game's scenario flowchart. Create new artwork based only on this description. The background is nearly black, covered in fine irregular chipped-paint and distressed metallic mottling. Color runs from muted emerald green at the left through dark teal in the middle to muted blue-violet at the right. Keep the central area much darker than the perimeter so bright game nodes and connecting lines placed over it remain readable. Across the center, between x=150 and 1130, y=230 and 490, put ONLY the exact English title 'PURGATORY' above 'CHAPTER', centered, in large heavy forward-slanted block capitals with wide tracking. Letters must be very low contrast, translucent-looking, dark muted emerald-to-teal-blue, merging into the grungy texture, with a faint soft glow. No Japanese characters. No menu heading, no buttons, no frame, no chart nodes, no icons, no extra words, no screenshot mockup, no border. Full-bleed opaque game background, straight-on, not a scene or photographed surface. Output exactly 1280x720 if possible.
