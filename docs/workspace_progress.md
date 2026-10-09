# SRW Z3 Rengoku-hen — English translation

Translation workspace for the supplied PS3 package
`JP0700-NPJB00689_00-SRWZ3RENDLGPKG00`.

Started on 2026-09-24 using the current English glossary from `../SRW Z3`.
The original package and sibling project remain untouched.

## Current progress

- Current scope includes battle speech and story dialogue. The
  battle catalog has 3,575 English drafts covering 5,113 stored occurrences;
  all received independent meaning proof, and 54 retain review notes.
- Non-dialogue translation contains 5,295 English entries and 182
  manual/artwork text blocks, with 9,177 source occurrences in the non-dialogue
  catalog. Every identified translatable catalog entry has English; 97 retain
  context or spelling review flags.
- Menus, mission conditions, names, descriptions, library entries, narration,
  chapter summaries, credits, terrain labels, inspected graphical labels and
  the manual are covered. Eight engine substitution keys remain intact.
  Character grids and binary false positives are excluded.
- Package, stage archive and licensed executable text extraction are complete.
  Original files remain unchanged. Raster and opaque-asset coverage is not
  exhaustive; the coverage report records the limits.
- The 1,168-entry sibling glossary snapshot is unchanged. Local additions and
  overrides bring the effective glossary to 1,320 entries.
- All 3,334 story records have English: 3,330 drafts and four review flags.
  Independent story meaning review remains pending.
- Source/catalog checks and 118 focused tests pass. Ten battle meaning fixes
  preceded the final terminology pass.

Read [the battle translation status](docs/battle_status.md),
[the English battle lines](docs/battle_lines_en.md),
[the non-dialogue status and reading copies](docs/non_dialogue_status.md),
[the English manual](docs/manual_en.md), [artwork labels](docs/artwork_en.md),
and [the handoff](HANDOFF.md). The earlier [opening draft](docs/opening_draft.md)
is retained separately.

English **test build 018** is available under `work/builds/rengoku_en_018/`:
a complete RPCS3 game folder and matching 12-file overlay for PS3 with CFW/HEN.
It uses Z3.1's Rodin Bold letters and compact terrain rendering. Both title
screen layouts now use Z3.1's English wordmark with a green Purgatory Chapter
subtitle, retaining the original animated Z. See [the title artwork](docs/title_screen_010.md).
The five Library buttons, Scenario Chart heading/background and all 15 chart
chapter labels are now English. See [the menu and chart changes](docs/library_chart_011.md).
Intermission now has an English heading and joined menu captions. Pilot List
uses MEL/DEF with clear footer spacing, and training uses Raise Stats,
Learn Skills and complete PP labels. Intermission and Pilot Info show bare
kill counts without Units. See [build 018's layout changes](docs/intermission_018.md).
Combo map popups now scale once with map zoom and fit one grid tile, making
the text larger when zoomed out. All five native graphics and their animation
are retained. See [build 017's sizing correction](docs/combo_popup_017.md).
Both battle fast-forward prompts read Fast within their original label space,
clearing the Cancel icon. See [build 016's control captions](docs/battle_controls_016.md).
Battle results label the total as Kills and omit the compact counter's
Units suffix, clearing the Level column.
See [build 015's results correction](docs/results_score_015.md).
Battle-animation subtitles now wrap before the right status icons: 464
entries / 609 occurrences receive word-preserving breaks at the same font
size. Forty-five longer entries remain pending separate storage/layout work.
See [build 014's subtitle evidence and limits](docs/battle_subtitles_014.md).
It uses compact battle-preview captions to clear weapon costs, Focus values
and the Attack badge on both factions, without reducing the font size. See
[build 013's changes and checks](docs/battle_preview_013.md).
It retains the No alignment correction with a live-pitch tab, verified against
Rengoku's actual font preset and native drawing instructions. The earlier
fix assumed the wrong glyph size and misplaced No by nine pixels. See
[build 012's diagnosis and tests](docs/confirmation_alignment_012.md).
It retains [build 009's selection and map-hover fixes](docs/screenshot_layout_009.md).
It retains [build 008's Team-view and settings-tab fixes](docs/screenshot_layout_008.md).
It retains [build 007's search, Effect wrapping and Unit-list fixes](docs/screenshot_layout_007.md).
It retains [build 006's narration, chapter art and vertical terrain fixes](docs/screenshot_layout_006.md).
It preserves [build 005's library and status fixes](docs/screenshot_layout_005.md).
It retains build 004's link-background fixes for dialogue and Back Log:
measured positions/widths, speaker-name boxes, and scene/glossary identity.
Read [the build status and instructions](docs/build_status.md). Archive
readback, executable structure, package hashes and RPCS3 offline decryption
checks pass. The user reached gameplay and Back Log in earlier builds;
build 018's final appearance and real console loading still need in-game checks.
The remaining 166 artwork/manual blocks have English source but are not inserted in images.
Original assets, installed games and saves are unchanged. The user-supplied
RAP was installed to fix the earlier RPCS3 license error.

## Files

| Path | Purpose |
|---|---|
| `localization/locales/en/STG*.json` | Canonical English, keyed to stable source IDs |
| `localization/locales/en/glossary.json` | Imported Z3 glossary wording and IDs |
| `localization/messages/glossary.json` | Imported source definitions |
| `localization/glossary_additions.json` | Researched Rengoku additions and explicit overrides |
| `analysis/glossary.json` | Base research/disambiguation metadata snapshot |
| `analysis/base_provenance.json` | Source paths and hashes of imported material |
| `localization/locales/en/non_dialogue.json` | Canonical non-dialogue English |
| `localization/locales/en/battle_lines.json` | Canonical battle subtitles and retreat quotes |
| `analysis/battle_line_pending.json` | Battle meanings, readings and wordplay needing further review |
| `analysis/battle_review_index.json` | Source-bound drafts and 45 independent meaning reports |
| `analysis/battle_terms.json` | Researched battle terminology and documented spelling decisions |
| `localization/locales/en/artwork.json` | Canonical manual and raster-text translations |
| `analysis/characters.json` | Cast research and source-bound library profiles |
| `analysis/non_dialogue_coverage.json` | Discovery inventory and explicit limits |
| `analysis/non_dialogue_pending.json` | Drafts needing spelling or context review |
| `analysis/non_dialogue_review_index.json` | Proof-report hashes and scope counts |
| `source/story/` | Ignored original Japanese records and member inventory |
| `work/pkg/` | Ignored pristine package extraction |
| `work/story/` | Ignored decrypted CPK and Lua originals |
| `work/batches/` | Ignored translation import proposals; not canonical after import |
| `tools/` | Extraction, glossary resolution, checking and preview tools |

## Working commands

Use Python with UTF-8 output. New environments need `requirements.txt`;
Python 3.11 or newer is recommended. The installed Python 3.8 worked for this
initial run but its cryptography dependency reports deprecation.

```powershell
python -X utf8 tools/localization.py check
python -X utf8 tools/non_dialogue.py check
python -X utf8 tools/verify_source.py
python -X utf8 -m unittest discover -s tests -v
python -X utf8 tools/report_non_dialogue.py
python -X utf8 tools/report_non_dialogue.py --write
python -X utf8 tools/localization.py preview
python -X utf8 tools/localization.py preview --write
```

Translation proposals can be checked and imported without building the game:

```powershell
python -X utf8 tools/localization.py apply work/batches/opening_0001.json
python -X utf8 tools/localization.py apply work/batches/opening_0001.json --write
```

Each proposal must contain either fully source-bound locale entries or a
`source_members` map of verified member SHA-256 hashes and exact record IDs.
Existing different translations are refused; intentional revisions belong
in the canonical locale file and must pass `check` afterward.

## Reproducing initial extraction

These commands require a fresh output workspace; extraction/seed tools refuse
to overwrite existing outputs. Always run each command without `--write` first
and inspect the preview before repeating with it.

```powershell
python -X utf8 tools/bootstrap.py --base "../SRW Z3"
python -X utf8 tools/bootstrap.py --base "../SRW Z3" --write
python -X utf8 tools/pkg_extract.py "<your-original.pkg>"
python -X utf8 tools/pkg_extract.py "<your-original.pkg>" --write
python -X utf8 tools/extract_story.py
python -X utf8 tools/extract_story.py --write
python -X utf8 tools/localization.py seed
python -X utf8 tools/localization.py seed --write
```

`bootstrap.py` copies only the canonical glossary data, research template,
CPK/dialogue readers and local `make_npdata.exe`. It never runs Z3's build,
deployment, emulator or older stage-preparation scripts.

The PKG reader supports the observed retail PS3 format only. Its format
references are RPCS3's [package implementation](https://github.com/RPCS3/rpcs3/blob/master/rpcs3/Crypto/unpkg.cpp)
and [header definitions](https://github.com/RPCS3/rpcs3/blob/master/rpcs3/Crypto/unpkg.h).
The SDAT decryptor is the existing local Hykem `make_npdata` v1.2; its hash is
recorded in `analysis/base_provenance.json`.

Non-dialogue extraction uses `prepare_non_dialogue.py`, `decrypt_eboot.py`,
`non_dialogue.py` and the guarded append-only `extend_non_dialogue_source.py`.
Inspect each tool's help and dry-run before writing. Do not reseed the existing
locale. Apply meaning reports before `normalize_non_dialogue_terms.py`;
exporters must honor occurrence overrides such as Defense/Defend.
