# English {{VERSION}} — {{SUMMARY}}

English patch for **Super Robot Taisen Z3: Rengoku-hen**, PS3 **NPJB00689**.
Built from local build {{BUILD_ID}}. {{TEST_RELEASE_STATUS}}

## Apply

Use [Retro Trans](https://github.com/retro-trans/retro-trans-tools/releases/latest),
refresh the catalog, browse to your original Japanese NPJB00689 PKG, and choose
Automatic > Latest (or {{VERSION}}). Save a NEW `.pkg` and install that output
through RPCS3. Alternatively download
`SRW-Z3-R-NPJB00689-English-{{VERSION}}-RPCS3.xdelta` and use Apply xdelta.

`BUILD-MANIFEST.json` is the standard Retro Trans v1 manifest with exact source,
output and patch identities. `SHA256SUMS.txt` verifies downloads;
`VALIDATION.json` records the whole-package decode round trip. Keep input and
output verification enabled. {{INSTALLATION_GUIDE_LINK}}

## What changed

{{CHANGE_LIST}}

## Coverage and limits

{{TRANSLATION_COUNTS_AND_REVIEW_FLAGS}}
{{UNINSERTED_ARTWORK_AND_SUBTITLE_LIMITS}}

## PS3 and RPCS3 compatibility

{{ACTUAL_RUNTIME_TEST_RESULTS}}
The patch requires your own game and matching license. No license data is
included. This modified PKG has cleared authentication and is for RPCS3;
it is not a signed console installer. Keep `dev_hdd0/game/NPJB00689`: for this
digital game it contains the game itself, not a disposable disc-install cache.
Distinguish format checks from gameplay and hardware acceptance.

## Validation

{{TEST_COUNTS_AND_PATCH_ROUNDTRIPS}}
{{PUBLIC_SOURCE_PROVENANCE_AND_MANIFEST_NOTES}}

## Acknowledgements and contribution

AI-assisted translation drafts are followed by terminology checks, editing
and playtesting. The Jigoku-hen project supplies glossary and tooling
references. Report translation/layout problems with a screenshot and version
at https://github.com/retro-trans/SRW-Z3-R/issues.

GitHub's Source code archives contain project sources. Use the patch asset
with your own game. No complete game image, original script dump, game file,
font, license or third-party tool binary is distributed.

<!-- Maintainer checklist: exact version/tag; reviewed source snapshot;
verified input/output hashes; whole-PKG round trip; native package extraction;
Retro Trans route/apply check; uploaded asset digests; regular numeric release
for catalog discovery; no original script catalogs or binary game data;
public-download validation and scoped catalog refresh. -->
