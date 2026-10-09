# Super Robot Taisen Z3: Rengoku-hen — English translation

English translation tools and PS3 patches for **Dai-3-Ji Super Robot Taisen Z:
Rengoku-hen / Purgatory Chapter**, Japanese digital release **NPJB00689**.

**Players:** download the [latest test release](https://github.com/retro-trans/SRW-Z3-R/releases)
and follow [the installation guide](docs/INSTALL.md). Apply the included xdelta
patches to your own matching pristine game folder. Each release includes exact
input/output hashes, download checksums, coverage and compatibility notes.

**Maintainers:** use [the release guide](docs/RELEASING.md) and
[release template](.github/RELEASE_TEMPLATE.md).

This project follows [retro-trans/SRW-Z3](https://github.com/retro-trans/SRW-Z3)
for documentation and patch distribution. Rengoku-hen has its own game ID,
font/layout adapters and executable offsets; Jigoku-hen patches cannot be used
with it. The public repository contains translations and project tools.
Original Japanese script catalogs and game data remain local.

## Current release and coverage

The first public English test release, **0.1.0**, packages verified local
**build 018**. It includes English story dialogue, battle subtitles, pilot,
mech and weapon text, library/glossary entries, mission conditions, menus,
Spirit/skill descriptions, narration and selected translated artwork.

| Area | Recorded coverage |
| --- | --- |
| Story | 3,334 records with English; independent meaning review pending |
| Battle text | 3,575 drafts covering 5,113 stored occurrences; independent meaning review complete, 54 review notes retained |
| Non-dialogue | 5,295 English entries covering 9,177 occurrences; 97 context/spelling flags retained |
| Glossary | 1,320 effective terms, including Rengoku additions and spelling overrides |
| Build checks | 118 tests, 173 rebuilt archive-member readbacks and three offline RPCS3 format checks passed |

Build 018 includes the English title screen, Library buttons, Scenario Chart,
chapter title screens and Intermission heading. It corrects dialogue and menu
alignment, terrain labels, stat columns, training tabs, battle captions,
confirmation choices and Combo popup sizing. See [release notes](docs/releases/0.1.0.md)
and [the build evidence](docs/build_status.md).

Coverage counts do not establish that every screen is translated or fully
proofread. **45 longer battle subtitle entries and 166 artwork/manual blocks
still need insertion/layout work.** Four story entries retain review flags.
Build 018's new appearance and real-console execution remain unverified;
earlier local builds received user gameplay reports.

## Install

The release ZIP contains **12 per-file xdelta patches**, a Python installer,
installation instructions and JSON manifests. It creates a new complete game
folder and verifies its files. You need Python 3.8+,
[xdelta3](https://github.com/jmacd/xdelta-gpl/releases), and your own pristine
NPJB00689 extraction. Preview first and then repeat with `--write`:

```powershell
python apply_release.py --source "D:/Games/NPJB00689-original" --out "D:/Games/NPJB00689-English" --xdelta "D:/Tools/xdelta3.exe"
```

See [INSTALL.md](docs/INSTALL.md) for the complete procedure and license setup.
This directory patch set is not a whole-ISO patch and does not support Retro
Trans's Automatic mode. The manifest identifies the supported source files.
GitHub's **Source code (zip)** contains project sources; use the release patch
ZIP to translate your game.

RPCS3 and modified PS3 use the same translated assets and fake SELF executable.
The game requires your own matching activation/license. Physical PS3 execution
and blanket CFW/HEN compatibility remain unverified. Stock firmware is not
supported by this test executable. No Vita build is included.

## Translation sources

| Path | Purpose |
| --- | --- |
| `localization/locales/en/STG*.json` | Story English, keyed by stable IDs |
| `localization/locales/en/battle_lines.json` | Battle dialogue English |
| `localization/locales/en/non_dialogue.json` | Menu, names, descriptions and library English |
| `localization/locales/en/artwork.json` | Translations for manual/raster text; insertion coverage is separate |
| `localization/locales/en/glossary.json` | Imported English glossary wording |
| `localization/glossary_additions.json` | Rengoku terminology and explicit overrides |
| `analysis/glossary.json` | Short glossary lookup keys and inherited research |
| `tools/`, `tests/` | Project-owned extraction, validation, build and focused test code |

Public locale exports omit original script text and local review-file paths.
English text, source fingerprints and IDs remain. See
[local source requirements](docs/LOCAL_SOURCE_DATA.md) before using build tools:
a fresh clone does not reconstruct all of the private catalogs and licensed
inputs needed for a complete game build. The maintained source workspace is
preserved separately.

Edit translation `text` fields by their existing ID. Preserve
`$$Japanese$$` glossary references, runtime placeholders, keyword links and
speech/internal-monologue wrappers. Source-dependent validation and builds
require the matching local catalogs; do not bypass those checks.

## Contribute and acknowledgements

Report bugs, proofreading corrections and playtesting results through
[GitHub issues](https://github.com/retro-trans/SRW-Z3-R/issues). Include the
release version, platform/runtime, affected screen and a screenshot.

Translation uses AI-assisted drafts followed by terminology checks, editing
and playtesting. The [Jigoku-hen project](https://github.com/retro-trans/SRW-Z3)
provides glossary, Rodin rendering and tooling references. Thanks to everyone
reporting translation and layout problems.

## Distribution

Release assets contain binary differences and support code/text. No complete
game, original Japanese script dump, extracted Lua, CPK/SDAT contents, licensed
font, RAP/RIF or downloaded third-party tool binary is included. Obtain those
inputs from your own game and their respective projects.
