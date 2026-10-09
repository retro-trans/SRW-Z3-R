# Public sources and local build inputs

The public repository contains the English translation, glossary lookup names,
project-owned Python tools, focused tests, installation instructions and release
metadata. Japanese script catalogs, extracted game assets, licensed fonts,
RAP/RIF data and third-party binary tools remain local.

The public checkout is exported to `work/publication/SRW-Z3-R` from the maintained
workspace. `publication_snapshot.py` removes original `source` text fields and
local batch/review paths from English locale exports. Stable message IDs,
English text, translation status, source fingerprints and runtime references
are preserved. It does not modify the maintained canonical files.

The source-bearing versions of `localization/locales/en/{battle_lines,
non_dialogue,artwork}.json`, `localization/messages/`, full analysis exports,
original script reading copies, `source/` and `work/` are not public build inputs.
Short Japanese glossary keys, `$$Japanese$$` references and focused UI examples
remain necessary for terminology resolution and source guards.

## Editing translations

Edit the `text` field in the public English locale by its existing message ID.
Keep placeholders, keyword link order, internal-monologue/speech wrappers and
`$$Japanese$$` glossary references. Submit translation or spelling corrections
through a pull request or an issue. Do not mint replacement IDs or edit hashes
to bypass source checks. Meaning review requires adjacent original context from
a maintainer's local catalog.

## Rebuilding

A fresh clone is not a complete game-building environment. The existing tools
require your own pristine NPJB00689 package/extraction, matching authenticated
executable and original source catalogs, fonts, offline RPCS3 tools, make_npdata,
and the read-only Jigoku-hen tooling reference. Some historical build helpers
also expect matching local analysis data. Restore your own local inputs and
follow `docs/build_status.md`; do not disable validation to bypass missing data.
There is no tested single-command bootstrap for all private inputs yet.

The first public patch repackages the already verified local build 018, which
was produced before Git initialization. Its manifest records the actual build
report digest and exact source/output identities. It does not invent a source
commit for that historical build. Publication commits identify the reviewed
public snapshot and release metadata, with source text removed as described.
