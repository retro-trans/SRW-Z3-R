# Super Robot Taisen Z3: Rengoku-hen — translation project

English translation tools and PS3 patches for **Dai-3-Ji Super Robot Taisen Z:
Rengoku-hen / Purgatory Chapter**, Japanese digital release **NPJB00689**.

**Players:** see [the installation guide](docs/INSTALL.md) and download
[the latest release](https://github.com/retro-trans/SRW-Z3-R/releases/latest).
Use [Retro Trans](https://github.com/retro-trans/retro-trans-tools) in Automatic
mode with your matching Japanese **NPJB00689 PKG**, or apply the downloaded
patch with DeltaPatcher or xdelta3. Save a new English PKG for CFW testing or RPCS3.
Each release lists installation steps, required input hashes, translation
coverage and compatibility notes.

**Maintainers:** use [the release guide](docs/RELEASING.md) and
[release template](.github/RELEASE_TEMPLATE.md).

This project follows [retro-trans/SRW-Z3](https://github.com/retro-trans/SRW-Z3)
for documentation and patch distribution. Rengoku-hen has its own game ID,
font/layout adapters and executable offsets; Jigoku-hen patches cannot be used
with it. The public repository contains translations and project tools.
Original Japanese script catalogs and game data remain local.

## Current release and coverage

**0.1.2** uses verified local **build 022**, including the corrections reported
during 0.1.1 testing and a CFW debug PKG candidate. **0.1.1 remains the first
public release.** Retro Trans supports both original and exact 0.1.1 PKG inputs.
DeltaPatcher and xdelta3 can apply the same patches.

| Area | Recorded coverage |
| --- | --- |
| Story | 3,334 English records; independent meaning review remains in progress |
| Battle | 3,575 drafts covering 5,113 stored occurrences; 54 review notes retained |
| Non-dialogue | 5,295 English entries covering 9,177 occurrences; 97 context/spelling flags retained |
| Glossary | 1,320 effective terms, including Rengoku overrides |
| Latest focused checks | 17 regressions, archive readbacks, three offline format checks, package authentication and all 77 installed file hashes passed |

The update fixes skill/Spirit descriptions, SR conditions and rewards, bonus
popups and selectors, highlighted-word spacing, terminology, ending dialogue
and credits. It adds Center/Wide Attack and Maximum Break artwork. Earlier
title, Library, Scenario Chart, Intermission and menu corrections remain.
See [release notes](docs/releases/0.1.2.md) and [validation notes](docs/validation/0.1.2.md).

Coverage does not establish every screen is translated or fully proofread.
Four story flags, 45 longer battle subtitles and 166 artwork/manual blocks
remain for review or insertion/layout work. New fixes and physical PS3 boot
still need gameplay confirmation.

## Install

Use [Retro Trans](https://github.com/retro-trans/retro-trans-tools) 0.5.1 or later:
refresh the catalog, select your original Japanese or exact English 0.1.1 PKG,
choose Automatic and Latest, Next or 0.1.2, then save a new English `.pkg`.
Manual [DeltaPatcher](https://github.com/marco-calautti/DeltaPatcher/releases/latest)
and [xdelta3](https://github.com/jmacd/xdelta/releases/latest) instructions are
in [INSTALL.md](docs/INSTALL.md), including input/output hashes.

The output is a debug PKG for CFW with fake/debug NPDRM SELF support, and its
77 files were verified after isolated RPCS3 installation. It is not Sony
retail-signed; stock firmware is unsupported and CFW boot is untested.
No general HEN compatibility is claimed. Use your original matching license.
Back up the installation and saves. Keep `dev_hdd0/game/NPJB00689`, since it
contains this digital game. No full game, license or Vita build is included.

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

## Contribute

Report bugs, proofreading corrections and playtesting results through
[GitHub issues](https://github.com/retro-trans/SRW-Z3-R/issues). Include the
release version, platform/runtime, affected screen and a screenshot.

## Credits

Translation uses AI-assisted drafts followed by terminology checks, editing
and playtesting. The [Jigoku-hen project](https://github.com/retro-trans/SRW-Z3)
provides glossary, Rodin rendering and tooling references. Thanks to everyone
reporting translation and layout problems.

## Distribution

Release assets contain binary differences and support code/text. No complete
game, original Japanese script dump, extracted Lua, CPK/SDAT contents, licensed
font, RAP/RIF or downloaded third-party tool binary is included. Obtain those
inputs from your own game and their respective projects.
