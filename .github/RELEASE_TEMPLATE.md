# English {{VERSION}} — {{SUMMARY}}

English patch for **Super Robot Taisen Z3: Rengoku-hen**, PS3 **NPJB00689**.
Built from local build {{BUILD_ID}}. {{TEST_RELEASE_STATUS}}

## Apply

Download `SRW-Z3-R-PS3-English-{{VERSION}}-file-patches.zip` and extract it.
Follow the included `INSTALL.md`; the input is your own matching pristine
NPJB00689 game folder. Preview first, then repeat with `--write`:

```powershell
python apply_release.py --source "D:/Games/NPJB00689-original" --out "D:/Games/NPJB00689-English" --xdelta "D:/Tools/xdelta3.exe"
```

`BUILD-MANIFEST.json` records every required input and output identity.
`SHA256SUMS.txt` verifies downloads; `VALIDATION.json` records full local
patch decode checks. This per-file package is not a whole-ISO patch or a
Retro Trans Automatic-mode release. Keep input verification enabled.

## What changed

{{CHANGE_LIST}}

## Coverage and limits

{{TRANSLATION_COUNTS_AND_REVIEW_FLAGS}}
{{UNINSERTED_ARTWORK_AND_SUBTITLE_LIMITS}}

## PS3 and RPCS3 compatibility

{{ACTUAL_RUNTIME_TEST_RESULTS}}
The patch requires your own game and matching license. No license data is
included. Physical PS3 requires a compatible modified setup; distinguish
offline checks from gameplay and hardware acceptance.

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
verified input/output hashes; every xdelta round trip; installer tested;
ZIP inventory; uploaded asset digests; correct prerelease state; no original
script catalogs or binary game data; actual public-download verification. -->
