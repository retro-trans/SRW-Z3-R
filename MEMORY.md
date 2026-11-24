# Persistent project memory

- User request, updated 2026-11-24: credit Retro Trans and show the version at
  the bottom-right of the title screen: `v<version>` above
  `github.com/retro-trans`. Keep the sibling-style small outlined two-line
  treatment, right-aligned with 28px right and 24px bottom margins. This
  supersedes the 2026-10-20 bottom-left request. Existing builds retain their
  recorded placement for verification; new builds use the bottom-right.
  Build032/v0.9.4 is the first new build after this placement change. Its
  packed footer, native decryption and 77 package/installed-file checks pass.
  The user explicitly requested publication of this release.
- Update this text for **every complete build**, including local test builds.
  `tools/build_game.py` automatically chooses the next semantic version from
  `build_version.json`, renders the footer in Rengoku's own title background,
  verifies it, and stamps `build_manifest.json` after complete readbacks pass.
  Preview/failed builds leave the counter unchanged. Optional `--version`
  must be newer than every successful issued build.
- User request, 2026-10-20: publish the next release as **0.9.0**. Use the
  explicit newer-version override when building; the in-game footer, build
  stamp, package proof and release must all say 0.9.0. After successful
  completion, automatic patch numbering continues with 0.9.1.
- Never package or release a newer version with an older footer. Check the
  packed member and stamp, not just a preview; package/release metadata must
  agree. Preserve previous builds and release assets. A new local build does
  not itself authorize publication.
- User spelling overrides: **Crowe Bluest**, **Elgan Roddick**, **Asakim Dowin**
  and **Daimon** where it names the unit. Keep full names and surname aliases
  consistent through `localization/glossary_additions.json`, naming rules and
  proofreading do-not-touch collections.
- Operation-condition display: retain Japanese in the native bounded buffers.
  The game adds fullwidth 1/2/3 prefixes and continuation padding before draw
  lookup. Keep all generated forms in the English lookup, not only the raw
  catalog strings. Validate with test_operation_build025.py and the read-only
  tools/check_operation_build.py against the compiled build.
- Spirit Command identities follow the sibling's canonical English: 直撃 is
  Break (Br), 闘志 is Fury (Fu). Preserve the unrelated Fighting Sp pilot skill
  and Rengoku's effects, targets, durations and SP costs. The alignment audit
  and dry-run-first fixer are analysis/spirit_alignment.json and
  tools/align_spirit_terms.py.
- Generated pilot bonuses and rewards (2026-11-24): translate bare skill
  `NAME +N` forms as well as `NAME LN+N` for the complete level-bearing
  skill category. Gold Bar amounts are composed natively; keep their source
  prefix/quantity fields unchanged and translate into owned draw storage.
  Both carryover variants must retain their own Z Chips behavior, live
  percentages and complete mechanics. The final no-SR Lua literal contains
  an explicit unknown escape: keep the raw source and its guarded observed
  runtime alias. Check tools/check_category031_build.py on packed outputs.
  Local build031/v0.9.3 and work/runtime_pkg_093 are complete; all 77 package
  and isolated installed files match. Use build_version.json for the next
  automatic version. Runtime screen confirmation remains pending.
- Audio/BGM layout (2026-11-22): label composites, button sprites, Play hints
  and option brackets are separate draws. Keep compact display overrides in
  tools/rengoku_audio_settings_layout.py; retain full canonical wording and
  native values/coordinates. Check packed captions with
  tools/check_audio_settings_build.py. Build029 was local 0.9.1; use the
  current build_version.json counter. Publication requires an explicit request.
- Battle captions (2026-11-24): keep SRVC.BIN and cue metadata Japanese and
  byte-identical to the original. The native subtitle field is 134 bytes and
  portrait state immediately follows; English atlas text can corrupt it.
  Supply complete converted-Japanese-to-English pairs only in owned draw
  storage via rengoku_battle_caption_runtime.py. Do not restore direct
  English SRVC insertion. Validate every compiled caption with
  tools/check_battle_caption_build.py and the native converter/draw tests.
  Mr. Advent/Mr. Blue remain in Setsuko's STG00015 lines until permission
  is granted at records 00016/00037 respectively.
  Earlier local build030/v0.9.2 is complete. Its
  local RPCS3 package is work/runtime_pkg_092. Public assets were not changed.
