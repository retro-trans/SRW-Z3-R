<!-- GitHub release title: {{VERSION}} — {{SUMMARY}} -->

English translation patch for **Super Robot Taisen Z3: Rengoku-hen** on PS3
(**NPJB00689**, Japanese digital release).

{{RELEASE_SUMMARY_AND_TEST_STATUS}}

### Apply

Use [Retro Trans](https://github.com/retro-trans/retro-trans-tools), version
{{MINIMUM_RETRO_TRANS_VERSION}} or later. Open **Automatic**, refresh the catalog,
and select {{SUPPORTED_INPUTS}}. Choose a new output filename and keep the source.

[DeltaPatcher](https://github.com/marco-calautti/DeltaPatcher) or
[xdelta3](https://github.com/jmacd/xdelta) can apply the same patch:

| Your source package | Patch |
| --- | --- |
| {{EXACT_SOURCE_EDITION_AND_VERSION}} | `{{PATCH_FILENAME}}` |

```text
xdelta3 -d -s "{{SOURCE_FILENAME}}" "{{PATCH_FILENAME}}" "{{OUTPUT_FILENAME}}"
```

In DeltaPatcher, enable **Backup original file** and **Checksum validation**.
{{INSTALLATION_GUIDE_LINK}}
Use the exact source package; compare a rejected input with
`BUILD-MANIFEST.json` and keep checksum verification enabled.

{{INPUT_AND_OUTPUT_BYTE_COUNTS_AND_SHA256}}

`BUILD-MANIFEST.json` records complete input/output identities.
`SHA256SUMS.txt` verifies downloads; `VALIDATION.json` records the local package
round trip. {{ACTUAL_PUBLIC_DOWNLOAD_AND_APPLY_RESULTS}}
Patch download: **{{PATCH_DOWNLOAD_SIZE}}**.

### What changed{{OPTIONAL_PREVIOUS_VERSION_SUFFIX}}

{{PLAYER_VISIBLE_CHANGE_LIST}}

{{FOCUSED_VALIDATION_SUMMARY_AND_VALIDATION_NOTES_LINK}}

### PS3 and RPCS3 compatibility

Install the output PKG through RPCS3's **File > Install Packages/Raps/Edats**.
Close RPCS3 and back up your installation first. Use your own matching license;
no RAP is supplied. Preserve savedata and other games. Keep
`dev_hdd0/game/NPJB00689`: this digital game's files are installed there.
Restart the game and load an in-game save when testing.

{{PACKAGE_SIGNING_AND_ACTUAL_RUNTIME_LIMITS}}
{{GAMEPLAY_AND_HARDWARE_STATUS_WITH_VALIDATION_NOTES_LINK}}

### What's included

{{TRANSLATION_COVERAGE_COUNTS_AND_REMAINING_REVIEW_WORK}}
{{ASSET_INVENTORY_AND_PLATFORM_LANGUAGE_LIMITS}}

### How it was translated

Drafts are AI-assisted and followed by terminology checks, editing and review
of playtesting reports. Community references guide names and terms.
Proofreading and corrections are welcome.

### Acknowledgements

{{VERIFIED_PROJECT_CREDITS_AND_REFERENCE_ACKNOWLEDGEMENTS}}

### Source code

GitHub's **Source code (zip)** contains project tools and English translation
sources. Download a `.xdelta` asset to patch your own game.
{{SOURCE_COMMIT_AND_RELEASE_TAG_PROVENANCE}}
Japanese script catalogs, game binaries, fonts and licenses are not published.

### Contribute

Report bugs, proofreading corrections and playtesting results through
[GitHub issues](https://github.com/retro-trans/SRW-Z3-R/issues).
Include the release version, runtime version, affected screen and screenshot.

---

No complete game package is included. Apply this patch to a game you own.

<!-- Follow docs/RELEASING.md and SRW-Z3 release 0.6.25's section order.
Use Rengoku-specific package identities, coverage, credits and compatibility.
Publish regular numeric versions for Retro Trans catalog discovery.
Keep exact source/output checks and asset digests; distinguish package/file
checks from gameplay/hardware results. Do not copy Jigoku-hen runtime claims. -->
