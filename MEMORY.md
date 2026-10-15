# Persistent project memory

- User request, 2026-10-10: credit Retro Trans and show the version on the
  lower-right of the press-any-button title screen, just like `../SRW Z3`:
  `v<version>` above `github.com/retro-trans`.
- Update this text for **every complete build**, including local test builds.
  `tools/build_game.py` automatically chooses the next semantic version from
  `build_version.json`, renders the footer in Rengoku's own title background,
  verifies it, and stamps `build_manifest.json` after complete readbacks pass.
  Preview/failed builds leave the counter unchanged. Optional `--version`
  must be newer than every successful issued build.
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
