# Persistent project memory

- User request, updated 2026-10-20: credit Retro Trans and show the version at
  the bottom-left of the title screen: `v<version>` above
  `github.com/retro-trans`. Keep the sibling-style small outlined two-line
  treatment, left-aligned at x28 with a 24px bottom margin. This replaces the
  previous lower-right placement. Existing builds retain their recorded
  placement for verification; newly completed builds use the bottom-left.
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
