# Changelog

## 2026-10-09 — Match SRW-Z3 release presentation

- Compare actual SRW-Z3 v0.6.25 and v0.6.24 release bodies, then align 0.1.1
  and the reusable template with the reference section order and title style.
- Add the source-to-patch table and download size. Keep the short player-facing
  checks on the release page and move detailed package/runtime evidence to
  docs/validation/0.1.1.md. Preserve DeltaPatcher and xdelta3 instructions.
- Match the README's player entry and separate credits/contribution sections.
  Verify section order against the actual reference, manifest identities,
  relative links and whitespace. Package assets and tag identity are unchanged.

## 2026-10-09 — Manual patching instructions

- Document Delta Patcher and xdelta3 alongside Retro Trans in the README,
  installation guide, first public release notes and reusable release template.
- Check Delta Patcher's upstream UI/source: Backup original file preserves the
  input and writes a PATCHED.pkg output; keep Checksum validation enabled.
- Run the documented xdelta3 -d -s command against the released patch: output
  matches the expected 721,946,688-byte PKG and SHA-256; original unchanged.
  Documentation links and whitespace checks pass. Release assets are unchanged.

## 2026-10-09 — First public release, English 0.1.1

- Publish the first public release with a standard Retro Trans v1
  original-PKG-to-English-PKG xdelta. Public release:
  https://github.com/retro-trans/SRW-Z3-R/releases/tag/v0.1.1.
  Translation/layout content uses verified local build 018.
- Verify all 77 PKG members, three package tests, complete xdelta decode and
  Retro Trans's actual recognizer, Latest/Next/specific routes and local
  apply_plan. All six downloaded public assets match local/server hashes.
  Scoped shared-catalog refresh succeeds and imports the exact manifest.
  Final actual apply through the live public catalog and public patch download
  produces the expected English PKG; the original remains unchanged.
- Bare patch: 191,578,190 bytes; SHA-256
  `fdf3d18da6b150548cf918968b5767c4f3fbd0ce258fe38fb3618cb0dd21886b`.
  English PKG: 721,946,688 bytes; SHA-256
  `dc570db31edda1928885ed5647e6a962f88e847eb309bcd2119978202ef39f3a`.
- Native isolated RPCS3 installation yields all 77 expected files including
  verified stage SDAT plaintext. Its headless shutdown assertion is recorded
  separately. The PKG has cleared authentication and targets RPCS3 only;
  no signed console-package or gameplay acceptance is claimed.
- Publish README, install/release guides and a reusable release template.
  Retain the extracted-folder workflow for local maintainer builds. No original package, canonical translation,
  user's installed game or save changes; previous remaining work is unchanged.

## 2026-09-26 — Intermission and pilot layouts, test build 018

- Translate the Intermission word sprite; join Team Setup, D-Trader,
  SR Points and Z Chips. Shorten Power Parts to Parts beside NEW and remove
  repeated deployment suffixes. Remove Intermission's score Units suffixes;
  the shared first-place suffix also disappears from Pilot Info.
- Use MEL/DEF without reducing type size, shift footer stat captions clear
  of numbers, join four training tab states as Raise Stats/Learn Skills,
  and use complete PP Held/PP Cost/PP Left rows.
- Review nine 80-record slices (720 in-slice, 780 unique with context),
  with 62 display overrides and 20 footer shifts. Canonical text is intact.
- All 118 tests, 173 member readbacks and three RPCS3 offline decrypt checks
  pass. Only AID members 0/1 change; previous executable and other archive
  plaintext are unchanged. See `docs/intermission_018.md` for bounds/scope.
- Complete RPCS3 folder and matching 12-file CFW/HEN overlay are in
  `work/builds/rengoku_en_018/`. ZIP: 75,776,024 bytes; SHA-256
  `4e41693ce38e0cef445275af637b0d33b13cdb117a7daee2b12405f438bb3bd2`.
- No installation/save changes. In-game appearance and real PS3 execution
  remain unverified. 45 longer subtitles and 166 artwork/manual blocks remain.

## 2026-09-26 — Combo popup size, test build 017

- Correct the Combo popup's double application of map zoom. Its original
  five English graphics now span a one-tile quad, preserving animation,
  centering, alpha and frame selection. At zoom 0.5 the label is 60% larger
  in each dimension. Other popup states retain their original scaling.
- Verify Rengoku's caller and quad drawer independently. All 114 tests,
  172 member readbacks and three RPCS3 offline decrypt checks pass.
  Only one four-byte executable branch and an 84-byte adapter change;
  archives, font, artwork and canonical catalogs match build 016.
- Package `work/builds/rengoku_en_017/` contains the complete RPCS3 folder
  and 12-file CFW/HEN overlay. ZIP: 75,826,968 bytes; SHA-256
  `5879d19a2cd8d7056244c88f76270095965185b006076a4e20db4ab2c9b2fc9c`.
- No installation/save changes. In-game appearance remains unverified;
  earlier pending work is unchanged. See `docs/combo_popup_017.md`.

## 2026-09-26 — Fast-forward control overlap, test build 016

- Shorten both matching Fast Forward captions to Fast at their original
  23px/21px font sizes, within the original four-cell label space. Preserve
  Cancel, button positions, styles and animation. Review: 90 records,
  including one 80-record slice and ten context rows; two display edits.
- All 110 tests, 172 member readbacks and three RPCS3 offline decrypt
  checks pass. Packed comparison changes only two pointers and 22 appended
  bytes in AID member 0; the other 15 AID members match 015. Executable,
  SRVC, font, artwork, stage plaintext and canonical catalogs are unchanged.
- Package `work/builds/rengoku_en_016/` contains the complete RPCS3 folder
  and 12-file CFW/HEN overlay. ZIP: 75,826,880 bytes; SHA-256
  `76df61ad0e847d2924729c28f52889428827e293620e878c0cc392871acdae60`.
- No installation/save changes. In-game appearance remains unverified;
  previous pending work is unchanged. See `docs/battle_controls_016.md`.

## 2026-09-26 — Results kill count label, test build 015

- Change the results column's two-piece Score heading to Kills and remove
  Units from its compact count widget, clearing the neighboring Level.
  Keep live totals, styles and positions. Pilot Info retains its separate
  Units label and the earlier size/position adjustment.
- Review two 80-record slices plus 20 adjacent records; three display
  pointers change with 13 appended bytes. Canonical catalogs stay intact.
- All 110 tests, 172 member readbacks and three offline RPCS3 decrypt
  checks pass. Only AID member 0 and regenerated stage encryption differ
  from 014. Executable, SRVC, font, artwork and story plaintext match.
- Complete RPCS3 folder and 12-file PS3 overlay are under
  `work/builds/rengoku_en_015/`. ZIP: 75,826,879 bytes; SHA-256
  `286864394316d989aeab947ff8c84f06ac3118a2e5eb43b5ec9d879b204775d2`.
- No installation/save changes. In-game appearance remains unverified.
  See `docs/results_score_015.md`; previous pending work is unchanged.

## 2026-09-26 — Battle-animation subtitle overflow, test build 014

- Wrap Blue's reported subtitle after “Mass-produced or not,” to clear
  the status panel. Keep wording, wrappers, font and canonical catalogs.
  Apply the same display-only rule to 464 unique SRVC entries / 609 stored
  occurrences, within 730px, two rows and the native 134-byte buffer.
- Examine 3,558 unique messages in 80-record slices. Leave 45 longer
  entries unchanged and flag their storage/layout work in the generated
  `SUBTITLE_LAYOUT.json`; no meaning edits or terminology decisions.
- All 108 tests, 172 member readbacks and three RPCS3 offline decrypt
  checks pass. Tests execute the native newline converter and read back
  all 6,356 voice cues with their metadata/order preserved.
- Package `work/builds/rengoku_en_014/`, with complete RPCS3 folder and
  12-file PS3 CFW/HEN overlay. ZIP: 75,826,869 bytes; SHA-256
  `ff94c20e434a12b8313092d2a3fc270c47107cdeb3abd8123f1025a0b610beb6`.
- Only SRVC and regenerated stage encryption differ from 013; executable,
  font, artwork, AID and stage plaintext match. No installation/save changes.
  In-game appearance remains unverified. See `docs/battle_subtitles_014.md`.

## 2026-09-26 — Battle-preview caption overflow, test build 013

- Fit the reported weapon-cost, Focus and Attack labels with Rnd., EN,
  Foc and Atk. Apply matching compact support/defense/re-attack and Song EN
  variants across 15 Rengoku FSSA records. Preserve font sizes, colors,
  positions, colons, live values and animation metadata.
- Verify actual 25/23/37px font presets and reproduce the original widths.
  Four new tests bring the suite to 104 passing checks. All 172 archive
  member readbacks and three RPCS3 offline decryption checks pass.
- Package `work/builds/rengoku_en_013/`, with complete RPCS3 folder and
  12-file PS3 CFW/HEN overlay. ZIP: 75,826,207 bytes; SHA-256
  `9041744285decff3a8d1ad3cdb9bc25ead7b9993263d5eecda0f7ce75ae6decd`.
- Packed AID changes only member 0's 15 string pointers and appended labels;
  other 15 members match 012. Executable is byte-identical to 012, retaining
  the No fix. Story plaintext, artwork and catalogs are unchanged.
- No installation/save changes. Visual gameplay acceptance remains pending.
  See `docs/battle_preview_013.md` for source evidence and review scope.

## 2026-09-26 — Correct No alignment regression, test build 012

- Reproduce the user's nine-pixel No overlap using the exact 009–011
  adapter. Confirmation preset 1 uses 28px glyph quads with 25px pitch;
  the previous fixed spacer incorrectly assumed both were 25px.
- Replace the blank spacer's advance with a live-pitch tab to column
  three. Slash/space then place No at column five, matching both active
  No overlays. All six Yes/No pairs pass native style/pen execution checks.
- Add four regression tests, including the failing old behavior, 144
  scale/origin cases, register preservation and all other glyph advances.
  All 100 tests, 172 member readbacks and three offline RPCS3 decrypt
  checks pass. The shipped adapter matches the tested code exactly.
- Complete build: `work/builds/rengoku_en_012/`, 78-file RPCS3 folder and
  matching 12-file CFW/HEN overlay. ZIP: 75,826,194 bytes; SHA-256
  `f1b0d960b2394c2dc67743313ebdffb0b695ec539635c03e0c6733e0c5c3592b`.
  Only executable and regenerated stage encryption differ from 011;
  stage plaintext, all other game files and all translations/artwork match.
- Gameplay appearance remains unverified. Originals, installed games,
  saves and prior builds are unchanged. See `docs/confirmation_alignment_012.md`.

## 2026-09-26 — Library menu and Scenario Chart, test build 011

- Translate all five title-screen Library buttons with Z3.1's Times Bold
  recipe, using Rengoku's independently verified sprite rectangles and all
  5,360 native animation references. Retain the build-010 English logo.
- Translate both chart heading copies and add a dark English Purgatory
  Chapter background generated with built-in image_gen. Preserve controls,
  nodes, connectors, borders and animation. Local artwork and full prompt
  are recorded in `localization/library_chart.json` and `docs/library_chart_011.md`.
- Resolve the chart's separately drawn episode prefix and wrapped title
  for all 15 chapters. Reuse canonical English and existing Unicode lookup;
  no dialogue edits or new executable code hooks. Longest title fits.
- All 96 tests, 172 member readbacks and three offline RPCS3 decrypt checks
  pass. Packed comparison changes only EFF members 131/132/133; other 133
  stored members match 010. Previous runtime code and story plaintext match.
- Built `work/builds/rengoku_en_011/`: 78-file complete RPCS3 folder and
  matching 12-file CFW/HEN overlay. ZIP is 75,826,144 bytes; SHA-256
  `96a851b7d4c14cab962ff1a191a22dbedf27d6ece2111e476c48a4e3dad28424`.
  Preview compositions checked; gameplay appearance and real PS3 loading
  still need validation. Original assets and builds 001–010 preserved.

## 2026-09-25 — English title artwork, test build 010

- Replace both title-screen wordmark/subtitle sprites with Z3.1's exact
  English gold wordmark and a new green PURGATORY / CHAPTER subtitle.
  Built-in image generation produced real-alpha lettering; its source,
  fitted sprite and prompt are retained locally.
- Independently identify Rengoku EFF member 133 and its 3,393 wordmark/
  subtitle animation references. Preserve native Z frame/fills, all other
  textures, geometry, timelines, English menu buttons and backgrounds.
- Five new source-backed tests bring the suite to 90 passing checks.
  All 170 rebuilt members and three offline RPCS3 decrypt checks pass.
  Final EFF comparison confirms all 135 other stored members unchanged;
  executable and story plaintext are identical to 009.
- Built `work/builds/rengoku_en_010/`: complete RPCS3 folder and 12-file
  CFW/HEN overlay. ZIP: 76,466,987 bytes; SHA-256
  `98bea26086db9fa3560e824b1c74c7def5e4de7f5cc8b4880da55f037030bb53`.
  Sprite proofs were visually checked; gameplay/transition and real PS3
  validation remain open. See `docs/title_screen_010.md`.

## 2026-09-25 — Command selection, map panel and Yes/No, test build 009

- Dim the inactive Ally/Enemy choice, retaining native faction palettes
  and matching both states' size, baseline and centering.
- Fit five map-hover Spirit strips into their original slots with 18
  compact labels whose masks match Z3.1 exactly. Preserve status indices,
  active overlays and native pitch. Fit narrow movement, Focus, support
  and recovery labels without moving their values.
- Align six selected Yes/No overlays with their background text. A blank
  measured cell preserves the original slash, No and cursor columns.
- Nine new regressions bring the suite to 85 passing tests. All archive
  readbacks and three independent RPCS3 offline decrypt checks pass.
  Final audit confirms 38 scoped FSSA edits and preservation of unrelated
  prior records, existing font masks, chapter art and PowerPC adapters.
- Built `work/builds/rengoku_en_009/`: complete RPCS3 folder and 12-file
  CFW/HEN overlay. ZIP: 76,298,090 bytes; SHA-256
  `78f259c63bc63a99efd42e9838168d0ac97bddcc40b3531a7e141317eee5768b`.
  Original assets, catalogs and earlier builds are unchanged. No gameplay
  or hardware test. See `docs/screenshot_layout_009.md`.

## 2026-09-25 — Team list and settings tabs, test build 008

- Fit six Team-view support headings using Z3.1's compact S. Atk / S. Def
  treatment, centered in Rengoku's original spans. Narrowest columns are
  72px apart; the resulting gap is about 10px. Preserve the separate,
  wider Unit-view headings fixed in 007.
- Shift the footer's bracket, movement value/slash and terrain types right
  together by 32px, leaving 10px after full-size Move and keeping the
  closing bracket inside the footer. Shorten all eight settings-tab states
  to Settings 1 / Settings 2, retaining original size/style/centering.
- Four new regressions bring the suite to 76 passing tests. All archive
  readbacks and three offline RPCS3 checks pass. Final artifact audit proves
  all 17 new edits, prior label preservation and byte-identical executable.
- Built `work/builds/rengoku_en_008/`: complete RPCS3 folder and 12-file
  CFW/HEN overlay. ZIP: 76,292,476 bytes; SHA-256
  `f14d99c2168e7eff44243c97fd0a970b64eaa13bcd4ed4f11aee0645f6eb71a6`.
  No installation/gameplay test. See `docs/screenshot_layout_008.md`.

## 2026-09-25 — Search and ally-list layout, test build 007

- Fit selected/inactive search tabs and result captions with Spirits and
  Abilities. Remove the extra SP Cost suffix while preserving the real SP
  column. Fit four Repair/Resupply pairs, both support-header pairs and both
  bottom Focus fields. All 26 FSSA edits retain native style and positions.
- Wrap all 204 Spirit/pilot-skill description bindings (187 distinct source
  strings) within 1,000px: <=2 Spirit lines, <=3 skill lines. Both Mind Resist
  variants become two lines. Preserve every word, condition and number;
  original RPW data and canonical English are unchanged.
- Five new regressions bring the suite to 72 passing tests. All 169 rebuilt
  archive members and untouched members verify; three offline RPCS3 checks
  pass. Final artifact audit confirms 26 menu labels and 187 description
  hooks. Stage plaintext and earlier fixes are retained.
- Built `work/builds/rengoku_en_007/`: complete RPCS3 folder and matching
  12-file CFW/HEN overlay. ZIP: 76,292,426 bytes, SHA-256
  `bb1bc54cd2bc6592635e808d17614024c8d5120ba6819b596cbe7dd1a071961a`.
  No installation or gameplay test. In-game placement remains unverified;
  see `docs/screenshot_layout_007.md` for evidence and recheck targets.

## 2026-09-25 — Narration, chapter artwork and vertical terrain, test build 006

- Fit all 32 timed narration rows within 96px side margins using actual
  Rodin widths. Preserve all row commands/timing and every word. Reflow two
  opening sentence pairs across existing rows; reduce glyphs to 32x36.
- Fix the multiline vertical terrain field (22 occurrences), preserving
  newline spacing, native geometry and both rating columns. Apply compact
  Air/Grd/Wtr/Spc at physical insertion and whole-field draw lookup.
- Insert all 15 canonical chapter title images with normal/glow copies.
  Translate numbered/final episode animations, including the finale's
  embedded title. Verify Rengoku-specific member IDs, mode words and quad
  counts; retain digits, timings, backgrounds, logos and unrelated artwork.
- Added six source-backed regressions. All 67 tests, 169 archive-member
  readbacks and three RPCS3 offline decrypt checks pass. Original assets,
  canonical English, earlier builds and story plaintext are preserved.
- Built `work/builds/rengoku_en_006/`: complete RPCS3 folder and 12-file PS3
  CFW/HEN overlay. ZIP is 76,292,291 bytes; SHA-256
  `6155adae1b7417948e4e52785c990804adcce9a1246ad132898ee274f6e15502`.
  No installation/gameplay test; visual fit and real hardware remain open.
  See `docs/screenshot_layout_006.md` for evidence and runtime checklist.

## 2026-09-25 — Library, stage heading and status layouts, test build 005

- Wrap ZKAN/MTFL library descriptions to Rengoku's measured 38-cell,
  1,140px panel; preserve every word and existing paragraph break. Retain
  nickname/CV alignment, create a gap before the value and fit the Face hint.
- Translate runtime-composed episode headings using the 15 cataloged titles,
  including Episode 1: Green Earth. Added 1,500 exact complete-string pairs.
- Apply one-cell terrain labels at physical insertion and native movement
  composition. Five compact masks match Z3.1's renderer pixel for pixel.
  MEL/RNG use normal-size Rodin glyphs; narrow Unit Info fields use Foc.
- Replace the four physical Ace Bonus fragments with one complete heading;
  change the pilot header to Spirits; enlarge and reposition Units.
- Added seven focused regression tests; all 61 tests pass. Built 005 in a new
  folder; 149 archive-member readbacks and three RPCS3 offline decrypt checks
  pass. Preserved originals, canonical wording, builds 001–004, story bytes
  and build 004's link runtime. Final appearance still requires gameplay QA.
- ZIP: `SRW_Z3_Rengoku_English_005_PS3_RPCS3_overlay.zip`, 20,503,528 bytes,
  SHA-256 `3d5d921dc8ed23ba65ba952cebf47e46ad4b746c8a2a3a391bd67a11162c4b61`.
  See `docs/screenshot_layout_005.md` for source sites and remaining checks.

## 2026-09-25 — Dialogue and Back Log link backgrounds, test build 004

- Adapted Z3.1's full link-background approach to independently verified
  Rengoku routines. Capture actual rendered widths for all 256 slots; use
  signed render-record coordinates and scene/glossary identity for dialogue
  selection; measure the separate speaker-name widget; fix normal dialogue's
  null scene context and translated glossary comparisons.
- Preserved the native 20-byte record layout, active-slot getter, colors,
  heights, draw tails and navigation. Rengoku's primary context lives in r28,
  so the adapted helper uses r27 as its counter. Source instructions and six
  complete blocks are guarded against the authenticated Rengoku executable.
- Added eight CPU regression tests, including real native registration,
  name geometry, all render slots and the old offscreen calculation. All
  54 tests pass; native metadata and live context checks pass.
- Built `work/builds/rengoku_en_004/` for RPCS3 and CFW/HEN PS3. All archive,
  source-preservation, SDAT round-trip and folder/overlay/ZIP checks pass.
  RPCS3 independently decrypted both stages and the new executable to exact
  expected bytes. No game was booted by the verification helper.
- ZIP: `SRW_Z3_Rengoku_English_004_PS3_RPCS3_overlay.zip`, 20,483,226 bytes,
  SHA-256 `2a1a4690bec6ccd04cd8c14a7bc29274d947852d0b1c691cee8fb0db04445cf8`.
- Font, catalog wording and source assets match 003. Besides EBOOT, only
  the stage's encryption bytes differ; decrypted stage content is unchanged.
  The user's new screenshots establish dialogue/Back Log in 003 and identify
  record 00004:00011 for retesting. Build 004's actual highlight rendering and
  real PS3 loading remain unverified. See `docs/link_backgrounds.md`.

## 2026-09-25 — Z3.1 font and screenshot fixes, test build 003

- Replaced Arial Regular with the local PS3 Rodin Latin Bold font using
  Z3.1's rendering recipe. All 95 printable ASCII masks and advances match
  the sibling renderer. Retained missing-symbol fallback and added six
  compact terrain/stat cells; inspected the finished 103-cell font proof.
- Found that centered text still used fixed character counts. Added a
  guarded Rengoku width-based centering adapter for the shifted setup help
  and map command labels. Added translation lookup after UTF-8 conversion,
  which had bypassed the old hook and left native labels Japanese.
- Added 324 exact levelled-skill variants and a scoped Ace Bonus fragment
  joiner. Moved Focus, aligned map summary colons, fitted Spirit Commands,
  centered information headings, and used Air/Grd/Sea/Spc and MEL/RNG in
  fixed stat slots. Native values and canonical translation text are intact.
- Added five tests that execute emitted PowerPC, including both encoding
  modes, active font metrics, register preservation, fallback and buffer
  reuse. All 46 tests pass. All 149 rebuilt CPK members, untouched members,
  SDAT round-trip, SELF structure and folder/overlay/ZIP checks pass.
- Built a new complete RPCS3 folder and 11-file PS3 CFW/HEN overlay under
  `work/builds/rengoku_en_003/`. RPCS3 independently decrypted the original
  stage, rebuilt stage and rebuilt executable to the expected bytes. The
  isolated verifier did not interrupt the user's running emulator.
- ZIP: `SRW_Z3_Rengoku_English_003_PS3_RPCS3_overlay.zip`, 20,482,475 bytes,
  SHA-256 `cc84400912c8af04bb39347dafccf74e23cc38aa9157192d0d2d80594df7937a`.
- User screenshots confirm build 002 reached gameplay after the license fix.
  Build 003's actual appearance and real PS3 loading remain unverified.
  Recheck the four screens and dialogue wrapping. The 182 artwork/manual
  blocks and existing translation review flags remain pending as documented.

## 2026-09-25 — RPCS3 startup license fix

- Diagnosed the user's 80029521 screenshot against the active emulator log.
  Build 002 reached game graphics/asset initialization, then the unchanged
  `DATA01.EDAT` failed because RPCS3 could not find the matching RAP.
- Installed the already supplied license at the exact active-user path logged
  by RPCS3, with dry-run preview, no overwrite and byte-identical readback.
  License contents were not exposed or added to build artifacts. No game or
  save files were changed. Updated the setup guide and future build README.
- A successful game restart remains unobserved; the same build can be retried.

## 2026-09-25 — RPCS3 and PS3 English test build 002

- Added dry-run-first Rengoku build and verification tools. Built a separate
  complete RPCS3 folder and an 11-file CFW/HEN PS3 overlay; original game and
  canonical translation files are unchanged. Nothing was installed or uploaded.
- Inserted all 3,334 story records, rebuilt 39 battle banks (5,077 translated
  SRVC occurrences; all 6,356 indexed cues checked), Lua/library/menu/credit
  fields and title metadata. Rebuilt and read back 149 CPK members.
- Located and guarded Rengoku's own font drawer, advance, keyword and Unicode
  routines. Added 97 Latin/symbol glyphs in empty cells on both font pages,
  proportional advances, and 9,830 exact text mappings in owned ELF storage.
  Preserved native placeholders, lookup keys, contextual overrides, system
  dialog UTF-8, ELF segment/TLS structure and application metadata.
- Build 002 fixes missing service-mark/circled-R glyphs found in build 001's
  visual font proof. Font source hashes and mapping are recorded in the build.
- All 41 tests pass. CPK readbacks, untouched-member checks, SDAT round-trip,
  executable guards and complete-folder/overlay/ZIP hashes pass. RPCS3 offline
  decryption independently produced the exact original stage, rebuilt stage
  and rebuilt ELF. Its sandbox startup hang was resolved by approved execution
  outside the sandbox; no game was booted.
- ZIP: `work/builds/rengoku_en_002/SRW_Z3_Rengoku_English_002_PS3_RPCS3_overlay.zip`
  (20,469,552 bytes), SHA-256
  `24243d97037e268faf43af968d02a152f8ed3b6ed1082f9e00720afa51b4e020`.
- Gameplay, real PS3 loading, layout and 3,571 draw-time consumer matches remain
  unverified. The 182 artwork/manual blocks remain untranslated in the actual
  images. Existing 155 translation review flags remain. See `docs/build_status.md`.

## 2026-09-25 — Remaining cataloged layout samples translated

- Translated the two quoted layout-test samples formerly excluded as dialogue.
  Independent meaning proof examined the 80-record slice and eight adjacent
  records; the two new English entries need no meaning or terminology fixes.
- Preserved source IDs and fingerprints, quotation wrappers, line breaks,
  ideographic spaces and the circled-number ruler. The source's 29-character
  diagnostic remains 29; it is not an English screen limit.
- Non-dialogue English now totals 5,295 entries, with 509 binary/character-grid
  exclusions and eight engine keys. No untranslated valid entries remain in
  the current story, battle, non-dialogue or artwork catalogs. Existing review
  flags remain: four story, 54 battle and 97 non-dialogue.
- Source and marker checks pass; all 9,177 non-dialogue bindings were freshly
  re-extracted, and artwork hashes and screenshot references verified. Only
  the two intended locale entries changed; other localization files and the
  source catalog are unchanged. Regenerated reading/status reports and updated
  current scope and glossary totals. Raster coverage and runtime fit remain
  unverified as documented in the handoff.

## 2026-09-25 — Story dialogue slices 8–42 (all records drafted)

- Sonnet sub-agents (at most four at once) drafted slices 8–42; every story
  record now has English: 3,330 drafts + 4 needs_review, 0 untranslated.
  Each agent examined its 80 rows plus 20 context rows per side.
- Orchestrator review per slice: punctuation/banner normalization, plain
  speaker names converted to glossary references, and meaning fixes
  (e.g. Crowe's germ joke, 惜しい事をした as regret, Blue's deliberate drop
  of さん, 乾杯/完敗 pun, Gun-Gun Leon chant, over-compressed 30-char wraps).
- Unified renderings across slices: "old man Sal", デンゼルの旦那 = Denzel,
  ley line lowercase, "The Cru—" for Gilter's cut-off insult.
- Glossary additions now 157 local entries, including in-game labels
  (Sidereal Soldier, Special Forces Soldier, Princess, Citizen, Insect,
  Firebug Trooper), places (Terminal/Central Base, Central Continent,
  Escole [provisional]), Sphere names (Lying Black Sheep, Bottomless Gourd),
  short Code names (Red/Black/White) and others.
- Checks: `localization.py check` 0 errors; 120 advisory notes (long lines
  56–72 chars, proposed terms); no record exceeds 4 lines; 30 tests pass;
  source verification passes. Runtime layout remains unverified.

## 2026-09-25 — Story dialogue slices 2–7

- User widened scope to story dialogue. Added `tools/story_slice.py`
  (dry-run-first packet builder: 80 rows, 20 context rows each side, matched
  glossary terms and character profiles) and `work/story_batches/BRIEF.md`.
- Sonnet sub-agents (at most four) drafted slices 2–7, flattened records
  80–559; each examined 120 records. Orchestrator reviewed, normalized
  punctuation (no full stop before 」/）, "..." for …), fixed a few meanings
  and wraps, then applied: 558 drafts, 2 needs_review, 2,774 untranslated.
- Glossary additions: Toby, Chief, Ley Line (matching in-game name/map
  labels; dialogue uses lowercase ley line), Lying Black Sheep (akurasu
  Sphere name), Firebug Trooper (in-game speaker label).
- Gilter Belone set to male per srw.wiki.cre.jp; slice 2's 『奴』 now
  『That guy』.
- Checks: `localization.py check` 0 errors, 18 long-line/line-count warnings
  (provisional guides, not measured limits); 30 tests pass. Runtime layout
  unverified.

## 2026-09-25 — Battle speech included; story dialogue excluded

- Followed the clarified scope and drafted all 3,575 identified battle lines,
  covering 5,113 stored occurrences. Story locales and original assets are
  unchanged. English is in `localization/locales/en/battle_lines.json`.
- Discovered Rengoku's own 39-bank SRVC offset table in its executable.
  Validated 6,356 indexed cues and preserved intact unused lines plus retreat
  quotes. Excluded 30 malformed unreferenced remnants and two binary matches.
- Completed 45 drafting slices and 45 independent meaning reports. Applied
  ten guarded meaning fixes; 54 English drafts retain explicit review notes.
- Added 69 glossary keys and one researched base-spelling override, bringing
  the effective glossary to 1,288. Added four character profiles (22 total).
  Applied reviewed name corrections after meaning proof and recorded the
  do-not-touch spellings. Imported glossary files remain unchanged.
- Generated battle reading/status documents and review/uncertainty indexes;
  updated non-dialogue coverage so battle text is no longer scope-excluded.
- Source, marker, glossary and preservation checks pass; 30 focused tests
  pass. No playable patch, runtime layout test or reinsertion was performed.

## 2026-09-25 — Non-dialogue English draft and coverage audit

- Honored the dialogue exclusion. Registered 9,177 occurrences and 5,812 grouped
  entries: 5,293 English drafts, eight engine keys and 511 explicit exclusions.
  No translatable catalog entry is empty; 97 retain review flags.
- Used the supplied RAP to extract executable text and verify all five program
  sections by HMAC. Original encrypted assets remain unchanged.
- Covered library, gameplay data, menus, conditions, headings, recaps,
  narration, credits, terrain labels and ten developer comments. Added 182
  manual and inspected artwork text blocks; original images are unchanged.
- Applied meaning fixes from 62 proof/classification reports before terminology
  normalization. Preserved runtime markers, full text and contextual
  Defense/Defend occurrence overrides.
- Expanded the effective glossary to 1,219 entries and the character database
  to 18 profiles. Recorded naming sources, uncertain readings, source history
  and a corrected artwork transcription.
- Classified 6,764 broad-scan candidates. Explicitly recorded heuristic scan
  limits, incomplete texture inspection and the opaque DATA01.EDAT.
- Generated category reading copies, manual/artwork documents, review index,
  pending-review list, coverage report and updated handoff.
- Re-extracted and checked all catalog bindings; verified artwork image hashes,
  screenshot references and original/story integrity. 22 focused tests pass.
  Runtime font/layout, relocation, image reinsertion and a playable patch
  remain unimplemented and unverified.


## 2026-09-24 — Translation workspace and opening draft

- Imported 1,168 current canonical Z3 English glossary entries, preserving
  source IDs, research metadata and input hashes. Added 13 Rengoku terms plus
  one explicit Elgan Rhodic spelling override, with the conflicting variants
  documented. Added initial cast research.
- Added dry-run-first bootstrap, retail PS3 package extraction, SDAT/CPK story
  extraction, source-bound English catalog import and readable-preview tools.
  Copied only the required CPK/dialogue reader modules and local SDAT tool.
- Extracted and verified 77 package files, 122 archive members and 3,334 Lua
  long-string records. Added an independent Lua lexer integrity audit.
- Drafted 80 records across opening episode 1 scripts and the start of the
  episode 2 story scene: 74 spoken/thought records and six banner records.
  Read 95 records including neighboring context. Kept 78 drafts and two
  explicit review flags; no rows marked reviewed or runtime-ready.
- Added checks for source hashes, stable IDs, glossary ambiguity, speakers,
  runtime placeholders, keyword-link labels/order and record structure.
  Draft review caught a reordered pair of keyword links before import; it was
  corrected and is now protected by a regression test. Japanese reading aids
  are distinguished from thought wrappers.
- Added ten focused passing tool tests, project instructions, extraction
  provenance, progress report, handoff and the English reading preview.
- Original package and sibling project unchanged; no game build, installation
  or publication performed. Font support, measured widths and insertion remain
  open work.
