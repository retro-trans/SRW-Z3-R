# Super Robot Taisen Z3: Rengoku-hen — translation project

English translation tools and PS3 patches for **Dai-3-Ji Super Robot Taisen Z:
Rengoku-hen / Purgatory Chapter**, Japanese digital release **NPJB00689**.

**Players:** see [the installation guide](docs/INSTALL.md) and download
[the latest release](https://github.com/retro-trans/SRW-Z3-R/releases/latest).
Use [Retro Trans](https://github.com/retro-trans/retro-trans-tools) in Automatic
mode with your matching Japanese **NPJB00689 PKG**, or apply the downloaded
patch with DeltaPatcher or xdelta3. Save a new English PKG for RPCS3.
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

**0.9.4** contains **build032**: corrected battle captions and portraits,
honorific context, settings/BGM layouts, generated skill/reward text,
carryover panels and a bottom-right version/Retro Trans footer.
**0.1.1 remains the first public release.**

English sources cover 3,334 story records, 3,575 battle entries and 5,295
non-dialogue entries, with selected translated artwork. Review flags, further
artwork/manual work and in-game confirmation remain. Coverage does not mean
every screen is translated or fully proofread.

The packed footer, archive readbacks, three native offline decryptions and
all 77 package/installed files pass. Gameplay and physical PS3 remain untested.
See [release notes](docs/releases/0.9.4.md) and [validation notes](docs/validation/0.9.4.md).

## Install

Use [Retro Trans](https://github.com/retro-trans/retro-trans-tools) 0.5.1 or later.
Refresh the catalog and choose **Latest** or **0.9.4**, starting from the
original Japanese NPJB00689 PKG or exact English public **0.9.0** PKG.
Older public packages can upgrade through existing release routes.
DeltaPatcher and xdelta3 can apply the same patches; see
[INSTALL.md](docs/INSTALL.md) for commands and exact package hashes.

The output is **RPCS3-only** with cleared authentication, not a Sony-signed or
CFW/HEN installer. Keep your matching license, installation and saves.
No full game or license is distributed.

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
