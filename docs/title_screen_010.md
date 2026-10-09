# English title screen — build 010

Request: translate the large title screen and smaller main-menu logo like
the English Z3.1 treatment. The main wordmark is the exact existing
`3rd SUPER ROBOT WARS` sprite from the read-only sibling project. The new
subtitle reads **PURGATORY / CHAPTER**, with white angular lettering and
green outlines matching Rengoku's green title palette.

This is a project translation of the subtitle, not an official English
game title. Producer Terada explains that 連獄 derives from 煉獄, between
heaven and hell, with a character substitution like the other Z3 subtitles.
The art rendering follows that meaning. [PlayStation producer interview](https://blog.ja.playstation.com/2015/04/02/20150402_srwz/).
The display wording and provenance are recorded in
`localization/title_screen.json`; existing prose catalogs use Rengoku-hen.

## Original resource and insertion

Rengoku's Lua constants independently identify `ScAnime_Z3TITLE_2D = 132`.
The corresponding resource is EFFPS3 member **133**, 21,055,856 bytes,
SHA-256 `e13739e4e1b893bb2dcd1eaddf3c15921b6d0d7efed6e9173c2d8c335460f95a`.
Its GTF begins at **0xecfe0**, with nine textures. Texture 1 is a 1024x720
linear ARGB32 atlas. These are Rengoku's own locations and counts.

Only two sprite rectangles change:

| Sprite | Rectangle x,y,w,h | Native animation references |
|---|---|---|
| Main wordmark | 0,0,706,296 | 1,721 |
| Subtitle | 0,603,339,117 | 1,672 |

The large and smaller menu layouts draw the same sprites, so all 3,393
references receive the English artwork. Geometry, sample rectangles,
colors, animation timelines, backgrounds, prompt and menu buttons retain
their original bytes. All four sampled native Z frame/fill rectangles are
verified byte for byte, including the one-frame intermediate fill and
transparent RGB where a Z sample overlaps wordmark padding.

`tools/rengoku_title_art.py` guards the source resource, exact reference
counts and local sprite hashes. The builder inserts it as one additional
EFF member, alongside the previous episode-title artwork. It refuses a
missing or changed art input instead of silently using Japanese art.

## Art files and image generation

- `work/title010_art/wordmark.png`: byte-identical to the sibling's reviewed
  706x296 RGBA sprite; SHA-256
  `294369bf76cdae6613224ec7887ff8438984111d58644a75825482fa27e81356`.
- `work/title010_art/subtitle-source.png`: built-in `image_gen` output,
  2135x737 RGBA with real transparency; SHA-256
  `441cbc4bd5abfb7868315bf717f886150e4eec63fb784e042bb73c6592f8f8d9`.
- `work/title010_art/subtitle.png`: cropped to generated alpha bounds,
  proportionally fitted to width 316 and placed at (8,5) in a 339x117 tile.
  Generated alpha is preserved; visible tile bounds are (8,5)-(324,84).
  SHA-256 `8fc8a17b5b3315b49eaf48414a27a8b855d69716bad63507c5ccca841d81375e`.

All bitmap files are ignored local build inputs. No original game assets
were sent to image generation. Its single reference was the sibling's
AI-created `work/title_logo_final/subtitle-v2.png`.

Exact built-in image-generation prompt:

> Use case: text-localization. Asset type: transparent game-title subtitle sprite. The input image is an AI-created subtitle style reference, not game data. Create a matching subtitle with exactly two lines: large dominant "PURGATORY" and smaller centered "CHAPTER" below. Spell PURGATORY P-U-R-G-A-T-O-R-Y. Preserve the reference's strongly slanted, heavy angular condensed uppercase lettering, white faces, crisp narrow contour-following dark outline and luminous double contour, but change all purple/violet to emerald green. Shape the outlines around each letter; no rectangular backing plate, no new icon, no logo, no third line, no Japanese. Wide compact lockup, similar proportions to the reference, with the lower line roughly 45% of the upper line's height. Pure white letter interiors, deep emerald outlines, restrained bright green edge glow. Genuine transparent RGBA background and transparent letter holes, never a checkerboard or solid backdrop. Leave a small transparent safety margin around all ink. Render clean, legible finished lettering suitable for resizing into a 339x117 sprite. Do not include the main Super Robot Wars logo or the Z.

## Validation

The atlas and both sprite-fit proofs in `work/title010_preview/` were
visually inspected. These proofs use the observed settled sprite quads;
they do not reproduce the game's animation transforms or claim live
gameplay validation. The previews also ship beside the completed build.

All 90 tests pass. Five focused tests check Rengoku's own title constant
and sample counts, exact Z/unrelated-byte preservation, real alpha and
the unchanged Z3.1 wordmark, both native layouts, and source/art drift
rejection. All 170 rebuilt members across nine archives were read back.
The final packed EFF contains the expected title resource, SHA-256
`2bb9623f098acfcf682e7f624f9eaaa03c2cfb1ff654f363bc3f88ea8e59f045`,
and all 135 other stored member payloads match build 009 exactly.

The executable and other game files match 009, except for regenerated
stage encryption; stage plaintext remains identical. Three independent
RPCS3 offline decryption checks pass. Complete game, 12-file overlay and
ZIP hashes agree. Source extraction and build-input catalogs were preserved.
Previous layout, font, dialogue and keyword fixes remain intact.

The complete output is `work/builds/rengoku_en_010/`. Its RPCS3 folder has
78 files including the extraction manifest, totaling 602,848,649 bytes.
The overlay ZIP is 76,466,987 bytes; SHA-256
`98bea26086db9fa3560e824b1c74c7def5e4de7f5cc8b4880da55f037030bb53`.
Evidence: `work/build010_dryrun.log`, `work/build010_tests.log`,
`work/build010_write.log`, and the build's `verification/RESULT.json`.

In-game checks remaining: large press-button logo, smaller menu logo,
transition/fiery-fill animation, alpha edges over the green backgrounds,
and real PS3 CFW/HEN loading. No emulator installation or save changes.
